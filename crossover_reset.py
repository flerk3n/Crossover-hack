#!/usr/bin/env python3
"""
CrossOver Reset Script
- Removes [Software\CodeWeavers\CrossOver\cxoffice] section from all bottles' system.reg
- Updates FirstRunDate in com.codeweavers.CrossOver.plist to current date/time
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime


# ── Paths ────────────────────────────────────────────────────────────────────
HOME            = Path.home()
BOTTLES_DIR     = HOME / "Library" / "Application Support" / "CrossOver" / "Bottles"
PLIST_PATH      = HOME / "Library" / "Preferences" / "com.codeweavers.CrossOver.plist"
TARGET_SECTION  = r"[Software\\CodeWeavers\\CrossOver\\cxoffice]"


# ── Helper: remove a section from a .reg file ────────────────────────────────
def remove_reg_section(reg_path: Path, section_header: str) -> bool:
    """
    Deletes the registry section that starts with `section_header`
    and all its key=value lines until the next section or EOF.
    Returns True if the section was found and removed.
    """
    try:
        text = reg_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"  [ERROR] Cannot read {reg_path}: {e}")
        return False

    # Escape special regex chars in the header (backslashes, brackets …)
    escaped = re.escape(section_header)

    # Pattern: the header line + everything up to (but not including) the
    # next section header  OR  end-of-string.
    # re.DOTALL lets '.' match newlines.
    pattern = rf"{escaped}.*?(?=\n\[|\Z)"
    new_text, count = re.subn(pattern, "", text, flags=re.DOTALL)

    if count == 0:
        print(f"  [INFO]  Section not found in {reg_path.name} – nothing to do.")
        return False

    # Clean up any double-blank lines left behind
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)

    try:
        reg_path.write_text(new_text, encoding="utf-8")
        print(f"  [OK]    Removed section from {reg_path}")
        return True
    except OSError as e:
        print(f"  [ERROR] Cannot write {reg_path}: {e}")
        return False


# ── Helper: update FirstRunDate in the plist ─────────────────────────────────
def update_plist_date(plist_path: Path) -> bool:
    """
    Sets the FirstRunDate key to the current date/time using the `defaults`
    command.  This is essential on macOS because the preferences daemon
    (cfprefsd) caches plist values in memory — writing the file directly
    with plistlib gets overwritten by the cached copy.  The `defaults` command
    talks to cfprefsd so the change actually sticks.
    """
    domain = plist_path.stem  # e.g. "com.codeweavers.CrossOver"

    # Read current value for display
    result = subprocess.run(
        ["defaults", "read", domain, "FirstRunDate"],
        capture_output=True, text=True
    )
    old_val = result.stdout.strip() if result.returncode == 0 else "<not set>"

    # Write the new date using `defaults write -date`
    # The -date flag stores it as a proper NSDate object (what CrossOver expects).
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S +0000")
    print(f"  [INFO]  FirstRunDate: '{old_val}'  →  '{now_str}'")

    result = subprocess.run(
        ["defaults", "write", domain, "FirstRunDate", "-date", now_str],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"  [ERROR] defaults write failed: {result.stderr.strip()}")
        return False

    print(f"  [OK]    Plist updated via `defaults write`.")
    return True


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  CrossOver Reset Script")
    print("=" * 60)

    # ── Step 1: Process every bottle ────────────────────────────────
    print(f"\n[1] Scanning bottles in:\n    {BOTTLES_DIR}\n")

    if not BOTTLES_DIR.exists():
        print("    [WARN] Bottles directory not found – skipping step 1.")
    else:
        bottles = [p for p in BOTTLES_DIR.iterdir() if p.is_dir()]
        if not bottles:
            print("    [INFO] No bottle folders found.")
        else:
            for bottle in sorted(bottles):
                reg_file = bottle / "system.reg"
                print(f"  Bottle: {bottle.name}")
                if reg_file.exists():
                    remove_reg_section(reg_file, TARGET_SECTION)
                else:
                    print(f"    [INFO] system.reg not found in this bottle.")

    # ── Step 2: Update plist ─────────────────────────────────────────
    print(f"\n[2] Updating plist:\n    {PLIST_PATH}\n")
    update_plist_date(PLIST_PATH)

    print("\n" + "=" * 60)
    print("  Done. Restart CrossOver for changes to take effect.")
    print("=" * 60)


if __name__ == "__main__":
    main()
