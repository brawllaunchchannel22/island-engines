# 🛠️ Trainz Universal Asset Fixer

A safe, non-destructive, open-source Python tool designed to fix common validation and script errors in **Trainz Railroad Simulator (TRS19, TRS22, Trainz Plus)**.

---

## 🛡️ Safety & Non-Destructive Design
* **Automatic Backups:** Creates `.bak` files before touching any configuration.
* **Dry-Run Mode:** Test what will be fixed before modifying any file with `--dry-run`.
* **Zero Asset Deletions:** Does not delete any meshes, sound files, or user assets.

---

## 🔧 What it Repairs
1. **VE146 (Legacy Bogeys):** Converts obsolete root `bogey` tags into modern `bogeys` containers without loss of orientation or reversed flags.
2. **Brace Syntax Errors:** Safely balances missing closing braces `}` in `config.txt`.
3. **VE179 (Invalid Region):** Removes invalid plaintext region tags (e.g. `"Europe"`, `"sodor"`).
4. **VE65 (Missing Textures):** Creates missing `.texture.txt` reference files.
5. **VE10 / VE103 (Missing Sounds):** Generates clean 44-byte silent PCM WAV stubs so engines don't throw missing sound errors.

---

## 🚀 How to Use

### 1. Requirements
* Python 3.7 or newer (Windows, Linux, or macOS).

### 2. Run Automatically (Auto-Detect Trainz Installation)
```bash
python3 trainz_universal_fixer.py
```

### 3. Test with Dry-Run Mode (Safe Preview)
```bash
python3 trainz_universal_fixer.py --dry-run
```

### 4. Fix a Specific Asset or Editing Folder
```bash
python3 trainz_universal_fixer.py --path "C:/path/to/your/editing/asset"
```
