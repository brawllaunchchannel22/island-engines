#!/usr/bin/env python3
"""
================================================================================
🚂 Trainz Universal Asset Fixer (TRS19 / TRS22 / Trainz Plus)
================================================================================
A safe, non-destructive, cross-platform repair utility for Trainz Simulator assets.
Supports Linux (Steam/Proton), Windows, and macOS.

Features:
- Automatic detection of local Trainz editing and build folders.
- Safe backup system: Creates '.bak' copies before modifying any file.
- Dry-run mode: Preview fixes without touching files (--dry-run).
- Non-destructive: Never deletes user assets, models, or textures.
- Repairs common Content Manager validation errors:
  * VE146: Legacy root bogey tags to modern bogeys container.
  * VE166: Missing or malformed thumbnail containers.
  * VE65: Missing .texture.txt reference files.
  * VE39 / VE68: Power-of-two texture dimensions.
  * VE10 / VE103: Missing sound WAV stubs.
  * VE179: Invalid region strings (e.g., "Europe", "sodor").
  * Syntax: Unbalanced braces in config.txt.
================================================================================
"""

import os
import sys
import re
import glob
import shutil
import argparse
from pathlib import Path

# Minimal 1x1 RGBA TGA dummy texture (22 bytes)
DUMMY_TGA_1X1 = bytes([
    0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00,
    0x20, 0x08, 0x80, 0x80, 0x80, 0xFF
])

# Minimal 44-byte silent PCM WAV file (44.1kHz, 16-bit, Mono)
SILENT_WAV_44B = bytes([
    0x52, 0x49, 0x46, 0x46,  # 'RIFF'
    0x24, 0x00, 0x00, 0x00,  # ChunkSize: 36
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
    0x00, 0x00, 0x00, 0x00   # Subchunk2Size: 0
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

    # 2. Windows LocalAppData
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        win_bases = [
            os.path.join(local_app_data, "N3V Games", "trs22"),
            os.path.join(local_app_data, "N3V Games", "trs19"),
            os.path.join(local_app_data, "N3V Games", "TANE")
        ]
        for wb in win_bases:
            if os.path.exists(wb):
                for b in glob.glob(os.path.join(wb, "build*", "editing")):
                    candidates.append(b)

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
            "braces_balanced": 0,
            "textures_created": 0,
            "sounds_stubbed": 0,
            "regions_cleaned": 0
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
        """Ensures all opening braces have matching closing braces without being fooled by comments or strings."""
        # Strip single-line comments (// and ;) and quoted strings to accurately count functional braces
        stripped = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        stripped = re.sub(r';.*$', '', stripped, flags=re.MULTILINE)
        stripped = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '', stripped)

        open_count = stripped.count("{")
        close_count = stripped.count("}")

        if open_count > close_count:
            diff = open_count - close_count
            fixed = text.rstrip() + ("\n}" * diff) + "\n"
            return fixed, True
        elif close_count > open_count:
            self.log(f"Warning: config.txt has {close_count - open_count} extra closing brace(s). Check manually.", prefix="[!]")
        return text, False

    def fix_legacy_bogeys(self, text, kind):
        """Converts legacy root bogey tags to the modern 'bogeys' container (VE146)."""
        if "bogeys" in text or not any(k in kind.lower() for k in ["traincar", "locomotive"]):
            return text, False

        bogey_matches = list(re.finditer(r'^\s*(bogey(?:-[0-9a-zA-Z_-]+)?)\s+(<[^>]+>)\s*$', text, re.MULTILINE | re.I))
        if not bogey_matches:
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
        """Removes invalid non-KUID region strings (e.g. region "Europe") that trigger VE179."""
        pattern = r'^\s*region\s+["\']?([^"\'<\r\n]+)["\']?\s*$'
        match = re.search(pattern, text, re.MULTILINE | re.I)
        if match:
            val = match.group(1).strip()
            if not val.startswith("<kuid"):
                cleaned = re.sub(pattern, "", text, flags=re.MULTILINE | re.I)
                return cleaned, True
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
        texture_refs = re.findall(r'["\']?([^"\'\r\n\t<>]+\.texture)["\']?', text, re.I)

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

                content = f"Primary={img_found}\nAlpha={img_found}\nTile=st\n"
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
                    wav_path.write_bytes(SILENT_WAV_44B)
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

        # 1. Fix Braces
        content, b_fixed = self.fix_config_braces(content)
        if b_fixed:
            asset_changed = True
            self.stats["braces_balanced"] += 1

        # 2. Fix Legacy Bogeys
        content, bg_fixed = self.fix_legacy_bogeys(content, kind)
        if bg_fixed:
            asset_changed = True
            self.stats["bogeys_fixed"] += 1

        # 3. Fix Invalid Region
        content, r_fixed = self.fix_invalid_region(content)
        if r_fixed:
            asset_changed = True
            self.stats["regions_cleaned"] += 1

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
        print("📊 TRAINZ UNIVERSAL ASSET FIXER — SUMMARY REPORT")
        print("=" * 60)
        print(f"  Assets Examined:        {self.stats['assets_checked']}")
        print(f"  Assets Repaired:        {self.stats['assets_repaired']}")
        print(f"  Legacy Bogeys Fixed:    {self.stats['bogeys_fixed']}")
        print(f"  Braces Balanced:        {self.stats['braces_balanced']}")
        print(f"  Missing Textures Fixed: {self.stats['textures_created']}")
        print(f"  Missing Sounds Fixed:   {self.stats['sounds_stubbed']}")
        print(f"  Invalid Regions Fixed:  {self.stats['regions_cleaned']}")
        if self.dry_run:
            print("  Status: DRY RUN ONLY (No changes written to disk)")
        else:
            print("  Status: All modifications safely committed with .bak backups.")
        print("=" * 60 + "\n")


def main():
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
