

# CrossOver Reset Script

A simple Python script for macOS that resets the CrossOver trial period.

## What it does

1. **Cleans registry** — Scans all your CrossOver bottles and removes the `[Software\CodeWeavers\CrossOver\cxoffice]` section from each bottle's `system.reg` file.
2. **Resets trial date** — Updates `FirstRunDate` in `com.codeweavers.CrossOver.plist` to the current system date and time.

## Usage

> Make sure CrossOver is **closed** before running.

```bash
python3 crossover_reset.py
```

If you hit a permissions error:

```bash
sudo python3 crossover_reset.py
```

After the script finishes, restart CrossOver for the changes to take effect.

## Requirements

- macOS
- Python 3 (pre-installed on macOS)
- No third-party libraries needed
