## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2024-05-25 - [Respectful Logging]
**Learning:** Cluttering the user's current working directory with log files creates friction and requires cleanup. Users expect tools to be "tidy" by default.
**Action:** Use standard state directories (like XDG_STATE_HOME) for logs and only surface the location when necessary (e.g., on failure or in summary).

## 2024-05-26 - [Batch Operation Error Visibility]
**Learning:** UX guidelines for CLI tools dictate that batch operations should aggregate and list specific failed items in the final summary output to prevent users from having to scroll up through extensive logs.
**Action:** When a batch process has failures, always list the failed item names (e.g. firmwares) in the final summary.
