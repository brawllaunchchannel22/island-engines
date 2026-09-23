#!/usr/bin/env python3
"""
================================================================================
Trainz Asset Fixer  (TRS19 / TRS22 / Trainz Plus)
================================================================================
A safe, non-destructive repair utility for Trainz Simulator content.
Works on Linux (Steam/Proton), Windows, and macOS.

What it actually does
  - VE146  : Converts old root bogey tags to the modern bogeys container.
  - VE65   : Creates missing .texture.txt stub files (uses existing image or
             a 1x1 dummy TGA so the validator stops complaining — the asset
             may still look broken until you supply a real texture).
  - VE10 / VE103 : Writes a silent WAV stub for missing sound references
             (the sound slot is filled, but it will be silent until replaced).
  - VE179  : Warns about invalid region values — does NOT auto-fix, because
             the right region KUID depends on your project (Sodor, real world,
             etc.) and must be set manually in Content Manager.
  - Braces : Warns about mismatched { } in config.txt — does NOT blindly
             append closing braces, as that could corrupt working configs.

What it does NOT do
  - VE39 / VE68 : No texture power-of-two resizing.
  - VE13 / VE48 : No category-class or trainz-build patching.
  - VE217 : No .m.reflect → .m.onetex renaming.

Safety
  - Creates .bak backup before touching any file (first run only).
  - Use --dry-run to preview everything without writing a single byte.
  - Path traversal protection on all file generation steps.
================================================================================
"""

import os
import sys
import re
import glob
import shutil
import argparse
from pathlib import Path

# 1x1 dummy TGA — 24-bit BGR, Top-Left origin flag (0x20 in image descriptor).
# More compatible with older TGA loaders in TRS19/TRS22 than RGBA variants.
DUMMY_TGA_1X1 = bytes([
    0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00,
    0x18, 0x20,              # PixelDepth: 24-bit, ImageDescriptor: Top-Left origin
    0x80, 0x80, 0x80         # 1 grey BGR pixel
])

# 1-sample silent WAV (46 bytes, 44.1kHz 16-bit Mono).
# ChunkSize = 38 (36 + 2 payload bytes), Subchunk2Size = 2 (1 sample × 2 bytes).
# The 0-byte version (44B) is rejected by some strict OpenAL/DirectX pipelines.
SILENT_WAV_46B = bytes([
    0x52, 0x49, 0x46, 0x46,  # 'RIFF'
    0x26, 0x00, 0x00, 0x00,  # ChunkSize: 38
    0x57, 0x41, 0x56, 0x45,  # 'WAVE'
    0x66, 0x6D, 0x74, 0x20,  # 'fmt '
    0x10, 0x00, 0x00, 0x00,  # Subchunk1Size: 16
    0x01, 0x00,              # AudioFormat: PCM (1)
    0x01, 0x00,              # NumChannels: 1
    0x44, 0xAC, 0x00, 0x00,  # SampleRate: 44100
    0x88, 0x58, 0x01, 0x00,  # ByteRate: 88200
    0x02, 0x00,              # BlockAlign: 2
    0x10, 0x00,              # BitsPerSample: 16
    0x64, 0x61, 0x74, 0x61,  # 'data'
    0x02, 0x00, 0x00, 0x00,  # Subchunk2Size: 2 bytes
    0x00, 0x00               # 1 sample of silence
])


def find_default_trainz_paths():
    """Auto-detects Trainz editing paths across Linux, Windows, and macOS."""
    candidates = []

    # 1. Linux Steam / Proton paths
    linux_bases = [
        os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/1784570/pfx/drive_c/users/steamuser/AppData/Local/N3V Games/trs22"),
        os.path.expanduser("~/.local/share/Steam/steamapps/compatdata/1784570/pfx/drive_c/users/steamuser/AppData/Local/N3V Games/trs22"),
        os.path.expanduser("~/.local/share/Steam/steamapps/compatdata/553520/pfx/drive_c/users/steamuser/AppData/Local/N3V Games/trs19"),
    ]
    for lb in linux_bases:
        if os.path.exists(lb):
            for b in glob.glob(os.path.join(lb, "build*", "editing")):
                candidates.append(b)

    # 2. Windows LocalAppData — also walk up to depth 3 for dynamic build numbers
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        n3v_root = os.path.join(local_app_data, "N3V Games")
        if os.path.exists(n3v_root):
            for root, dirs, _ in os.walk(n3v_root):
                depth = root.replace(n3v_root, "").count(os.sep)
                if depth >= 3:
                    dirs.clear()  # prune
                    continue
                for d in dirs:
                    if d.lower() == "editing":
                        candidates.append(os.path.join(root, d))

    # 3. macOS Application Support
    mac_bases = [
        os.path.expanduser("~/Library/Application Support/com.n3vgames.trs22"),
        os.path.expanduser("~/Library/Application Support/com.n3vgames.trs19")
    ]
    for mb in mac_bases:
        if os.path.exists(mb):
            for b in glob.glob(os.path.join(mb, "build*", "editing")):
                candidates.append(b)

    return sorted(list(set(candidates)))


class TrainzAssetFixer:
    def __init__(self, dry_run=False, make_backups=True, verbose=True):
        self.dry_run = dry_run
        self.make_backups = make_backups
        self.verbose = verbose
        self.stats = {
            "assets_checked": 0,
            "assets_repaired": 0,
            "bogeys_fixed": 0,
            "textures_created": 0,
            "sounds_stubbed": 0,
            "regions_warned": 0
        }

    def log(self, msg, prefix="[*]"):
        if self.verbose:
            print(f"{prefix} {msg}")

    def read_text_file(self, file_path):
        """Reads a text file with multi-encoding fallback (utf-8-sig, utf-8, windows-1252, latin-1)."""
        encodings = ["utf-8-sig", "utf-8", "windows-1252", "latin-1"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read(), enc
            except (UnicodeDecodeError, LookupError):
                continue
            except Exception as e:
                self.log(f"Error reading {file_path}: {e}")
                return None, None
        
        # Final fallback with error replacement
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read(), "utf-8"
        except Exception as e:
            self.log(f"Fatal error reading {file_path}: {e}")
            return None, None

    def safe_write_text(self, file_path, content, encoding="utf-8"):
        """Safely writes text to file, creating a backup on first modification."""
        if self.dry_run:
            self.log(f"[DRY-RUN] Would update: {file_path.name}")
            return True

        if self.make_backups:
            bak_path = file_path.with_suffix(file_path.suffix + ".bak")
            if not bak_path.exists():
                try:
                    shutil.copy2(file_path, bak_path)
                except Exception as e:
                    self.log(f"Warning: Could not create backup for {file_path.name}: {e}")

        try:
            with open(file_path, "w", encoding=encoding, errors="replace") as f:
                f.write(content)
            return True
        except Exception as e:
            self.log(f"Error writing to {file_path}: {e}")
            return False

    def fix_config_braces(self, text):
        """Checks for unbalanced { } in config.txt and warns — does not auto-fix.
        Blindly appending closing braces at the end of a file is risky: the missing
        brace could belong anywhere in the middle of the config, not at the end."""
        # Strip comments and quoted strings before counting braces
        stripped = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        stripped = re.sub(r';.*$', '', stripped, flags=re.MULTILINE)
        stripped = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '', stripped)

        open_count = stripped.count("{")
        close_count = stripped.count("}")

        if open_count > close_count:
            diff = open_count - close_count
            self.log(
                f"config.txt has {diff} unclosed brace(s) — please fix manually. "
                f"(Auto-appending would likely place the '}}' in the wrong spot.)",
                prefix="[!]"
            )
        elif close_count > open_count:
            self.log(
                f"config.txt has {close_count - open_count} extra closing brace(s) — check manually.",
                prefix="[!]"
            )
        return text, False


    def fix_legacy_bogeys(self, text, kind, config_file=None):
        """Converts legacy root bogey tags to the modern 'bogeys' container (VE146).

        Uses a regex to detect an existing bogeys { } block so that a comment or
        username containing the word 'bogeys' doesn't cause the fix to be skipped.
        Forces a backup of config.txt before writing, regardless of --no-backup,
        because bogey conversion is the riskiest structural change this tool makes.
        """
        if not any(k in kind.lower() for k in ["traincar", "locomotive"]):
            return text, False

        # Skip only if an actual bogeys block already exists (not just the word in a comment)
        if re.search(r'^\s*bogeys\s*\{', text, re.MULTILINE | re.I):
            return text, False

        bogey_matches = list(re.finditer(r'^\s*(bogey(?:-[0-9a-zA-Z_-]+)?)\s+(<[^>]+>)\s*$', text, re.MULTILINE | re.I))
        if not bogey_matches:
            return text, False

        # Force a backup before bogey conversion — this is the riskiest change
        if config_file is not None and not self.dry_run:
            bak_path = config_file.with_suffix(config_file.suffix + ".bak")
            if not bak_path.exists():
                try:
                    import shutil as _shutil
                    _shutil.copy2(config_file, bak_path)
                    self.log(f"Forced backup before bogey conversion: {bak_path.name}", prefix="[B]")
                except Exception as e:
                    self.log(f"Could not create forced backup — skipping bogey conversion: {e}", prefix="[x]")
                    return text, False

        containers = []
        new_text = text

        for i, match in enumerate(bogey_matches):
            tag_name = match.group(1).lower()
            kuid_val = match.group(2)
            rev_val = "1" if "reversed" in tag_name or tag_name.endswith("-r") else "0"

            c_name = f"bogey_{i}"
            containers.append(f"""  {c_name}
  {{
    bogey                               {kuid_val}
    reversed                            {rev_val}
  }}""")
            # Remove legacy tag
            new_text = new_text.replace(match.group(0), "")

        bogey_block = "bogeys\n{\n" + "\n".join(containers) + "\n}\n"
        new_text = new_text.rstrip() + "\n\n" + bogey_block
        return new_text, True

    def fix_invalid_region(self, text):
        """Warns about invalid non-KUID region strings (VE179) without auto-deleting.
        Region KUIDs are project-specific (e.g. Sodor vs. real world) and cannot be
        safely guessed by a script — manual setting in Content Manager is required."""
        pattern = r'^\s*region\s+["\']?([^"\'<\r\n]+)["\']?\s*$'
        match = re.search(pattern, text, re.MULTILINE | re.I)
        if match:
            val = match.group(1).strip()
            if not val.startswith("<kuid"):
                self.log(
                    f"Ungültiger region-Tag gefunden ('{val}') – bitte manuell im "
                    f"Content Manager auf eine gültige Region-KUID setzen (VE179).",
                    prefix="[!]"
                )
                return text, True  # True = warning was issued; text unchanged
        return text, False

    def is_safe_subpath(self, base_dir, target_path):
        """Verifies that target_path is strictly inside base_dir to prevent path traversal."""
        try:
            base_resolved = base_dir.resolve()
            target_resolved = target_path.resolve()
            # Python 3.9+ is_relative_to, with relative_to fallback
            if hasattr(target_resolved, "is_relative_to"):
                return target_resolved.is_relative_to(base_resolved)
            target_resolved.relative_to(base_resolved)
            return True
        except (ValueError, RuntimeError):
            return False

    def fix_missing_texture_files(self, asset_dir, text):
        """Generates missing .texture.txt files referenced in config.txt (VE65) with traversal protection."""
        fixed_count = 0
        texture_refs = [r.strip(" \"';") for r in re.findall(r'["\']?([^"\'\r\n\t<>]+\.texture)["\']?', text, re.I)]

        for ref in texture_refs:
            ref_clean = ref.strip().replace("\\", "/").lstrip("/")
            tex_txt_path = asset_dir / f"{ref_clean}.txt"

            # Security check: prevent directory traversal
            if not self.is_safe_subpath(asset_dir, tex_txt_path):
                self.log(f"Security: Blocked path traversal attempt in texture ref: {ref}", prefix="[x]")
                continue

            if not tex_txt_path.exists():
                stem = ref_clean[:-8] if ref_clean.lower().endswith(".texture") else ref_clean
                base_name = os.path.basename(stem)
                target_dir = tex_txt_path.parent

                # Look for matching image file with deterministic priority (.tga > .bmp > .png > .jpg)
                search_dirs = [target_dir, asset_dir] if target_dir != asset_dir else [asset_dir]
                img_found = None

                ext_priority = {".tga": 0, ".bmp": 1, ".png": 2, ".jpg": 3, ".jpeg": 4}
                for s_dir in search_dirs:
                    if not s_dir.exists():
                        continue
                    candidates = [
                        c for c in s_dir.glob(f"{base_name}.*")
                        if c.suffix.lower() in ext_priority
                    ]
                    if candidates:
                        # Sort deterministically by extension priority, then lower-case file name
                        candidates.sort(key=lambda p: (ext_priority.get(p.suffix.lower(), 99), p.name.lower()))
                        img_found = candidates[0].name
                        break

                if not img_found:
                    # Create safe fallback dummy TGA in the same directory as the texture.txt
                    dummy_tga_path = target_dir / f"{base_name}.tga"
                    if not self.is_safe_subpath(asset_dir, dummy_tga_path):
                        continue
                    if not dummy_tga_path.exists() and not self.dry_run:
                        target_dir.mkdir(parents=True, exist_ok=True)
                        dummy_tga_path.write_bytes(DUMMY_TGA_1X1)
                    img_found = f"{base_name}.tga"

                content = f"Primary={img_found}\nTile=st\n"
                if not self.dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    tex_txt_path.write_text(content, encoding="utf-8")
                fixed_count += 1

        return fixed_count

    def fix_missing_wav_files(self, asset_dir, text):
        """Generates silent PCM WAV stubs for referenced missing sounds (VE10/VE103) with traversal protection."""
        fixed_count = 0
        wav_refs = re.findall(r'["\']?([^"\'\r\n\t<>]+\.wav)["\']?', text, re.I)

        for ref in wav_refs:
            clean_wav = ref.strip().replace("\\", "/").lstrip("/")
            wav_path = asset_dir / clean_wav

            # Security check: prevent directory traversal
            if not self.is_safe_subpath(asset_dir, wav_path):
                self.log(f"Security: Blocked path traversal attempt in wav ref: {ref}", prefix="[x]")
                continue

            if not wav_path.exists():
                if not self.dry_run:
                    wav_path.parent.mkdir(parents=True, exist_ok=True)
                    wav_path.write_bytes(SILENT_WAV_46B)
                fixed_count += 1

        return fixed_count

    def repair_asset_folder(self, folder_path):
        """Repairs a single asset folder containing config.txt."""
        folder = Path(folder_path)
        config_file = folder / "config.txt"
        if not config_file.exists():
            return False

        self.stats["assets_checked"] += 1
        asset_changed = False

        content, detected_enc = self.read_text_file(config_file)
        if content is None:
            return False

        # Extract basic info
        kind_m = re.search(r'^\s*kind\s+["\']?([^"\r\n]+)', content, re.MULTILINE | re.I)
        kind = kind_m.group(1).strip() if kind_m else ""
        name_m = re.search(r'^\s*username\s+["\']?([^"\r\n]+)', content, re.MULTILINE | re.I)
        name = name_m.group(1).strip() if name_m else folder.name

        # 1. Check Braces (warn only, no auto-fix)
        content, b_fixed = self.fix_config_braces(content)
        # fix_config_braces always returns False — braces not auto-fixed

        # 2. Fix Legacy Bogeys (forced backup happens inside if needed)
        content, bg_fixed = self.fix_legacy_bogeys(content, kind, config_file=config_file)
        if bg_fixed:
            asset_changed = True
            self.stats["bogeys_fixed"] += 1

        # 3. Check Invalid Region (warn only)
        content, r_fixed = self.fix_invalid_region(content)
        if r_fixed:
            self.stats["regions_warned"] += 1

        # 4. Save config.txt if modified
        if asset_changed:
            self.safe_write_text(config_file, content, encoding=detected_enc or "utf-8")

        # 5. Fix Missing Textures
        tex_fixed = self.fix_missing_texture_files(folder, content)
        if tex_fixed > 0:
            asset_changed = True
            self.stats["textures_created"] += tex_fixed

        # 6. Fix Missing Sounds
        snd_fixed = self.fix_missing_wav_files(folder, content)
        if snd_fixed > 0:
            asset_changed = True
            self.stats["sounds_stubbed"] += snd_fixed

        if asset_changed:
            self.stats["assets_repaired"] += 1
            self.log(f"Repaired: {name} ({folder.name})", prefix="[✓]")

        return asset_changed

    def scan_and_repair(self, target_path):
        """Scans a directory of open/editing Trainz assets and repairs them safely."""
        target = Path(target_path).resolve()
        if not target.exists():
            self.log(f"Path does not exist: {target}", prefix="[x]")
            return

        self.log(f"Starting scan in: {target}")
        if self.dry_run:
            self.log("MODE: DRY RUN (No files will be altered)")

        # Check if target is a single asset folder or a container of assets
        if (target / "config.txt").exists():
            self.repair_asset_folder(target)
        else:
            for item in sorted(target.iterdir()):
                if item.is_dir() and (item / "config.txt").exists():
                    self.repair_asset_folder(item)

        self.print_summary()

    def print_summary(self):
        print("\n" + "=" * 60)
        print("TRAINZ ASSET FIXER — SUMMARY REPORT")
        print("=" * 60)
        print(f"  Assets scanned:         {self.stats['assets_checked']}")
        print(f"  Assets changed:         {self.stats['assets_repaired']}")
        print(f"  Bogeys converted:       {self.stats['bogeys_fixed']}")
        print(f"  Texture stubs created:  {self.stats['textures_created']}")
        print(f"  Sound stubs created:    {self.stats['sounds_stubbed']}")
        print(f"  Region warnings:        {self.stats['regions_warned']}")
        if self.dry_run:
            print("  Mode: DRY RUN — no files were written")
        else:
            print("  Mode: LIVE — .bak backups created before each change")
        print("=" * 60 + "\n")



DISCLAIMER = """
================================================================================
 USE AT YOUR OWN RISK
 This script modifies Trainz content files. The author takes no responsibility
 for broken assets, corrupted configs, or any other damage caused by running it.
 Always run with --dry-run first and keep your own backups.
================================================================================
"""

def main():
    print(DISCLAIMER)
    parser = argparse.ArgumentParser(
        description="Trainz Universal Asset Fixer — Safe, non-destructive repair tool for TRS19/TRS22."
    )
    parser.add_argument(
        "--path", "-p",
        help="Path to an open asset folder or editing directory. If omitted, auto-detects installed Trainz directories."
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Simulate the repairs and print proposed changes without touching any files."
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable creation of '.bak' backup files (not recommended)."
    )

    args = parser.parse_args()

    fixer = TrainzAssetFixer(
        dry_run=args.dry_run,
        make_backups=not args.no_backup,
        verbose=True
    )

    if args.path:
        fixer.scan_and_repair(args.path)
    else:
        detected = find_default_trainz_paths()
        if not detected:
            print("[!] No default Trainz editing directories detected.")
            print("[!] Please specify a path manually using: python trainz_universal_fixer.py --path <path_to_assets>")
            sys.exit(1)

        print(f"[*] Found {len(detected)} Trainz editing folder(s):")
        for d in detected:
            print(f"    - {d}")
        print()

        for d in detected:
            fixer.scan_and_repair(d)


if __name__ == "__main__":
    main()
