# CrossOver Configuration Refresh

A small macOS utility for refreshing selected CrossOver configuration data for
the current user.

## Behavior

When run, the script:

1. Finds each bottle in `~/Library/Application Support/CrossOver/Bottles`.
2. Removes the `[Software\CodeWeavers\CrossOver\cxoffice]` registry section
   from a bottle's `system.reg`, when present.
3. Updates the `FirstRunDate` preference in
   `~/Library/Preferences/com.codeweavers.CrossOver.plist` to the current local
   date and time, using macOS's `defaults` command.

The script prints the outcome for every bottle and verifies the updated
preference value before it finishes.

## Before you run it

- Quit CrossOver completely so it is not writing to its bottle or preference
  files at the same time.
- Back up any bottles you care about. `system.reg` files are modified in place.
- Run the script as the same macOS user whose CrossOver installation you want
  to maintain.

## Usage

From this project directory, run:

```bash
python3 crossover_reset.py
```

Do **not** use `sudo`. The script operates on paths beneath the invoking
user's home directory; `sudo` would instead target root's CrossOver
configuration.

Restart CrossOver after the script completes.

## Requirements

- macOS
- Python 3
- The built-in `defaults` command

No third-party Python packages are required.

## Notes

- Missing bottle folders, `system.reg` files, or registry sections are reported
  and skipped.
- If the CrossOver preference domain does not yet exist, `defaults` creates the
  `FirstRunDate` preference when the script runs.
