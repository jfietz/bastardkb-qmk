## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2026-02-15 - [Actionable Log Feedback]
**Learning:** Build tools often bury the path to detailed log files, forcing users to scroll back or guess where logs are stored. Adding a direct, stylized path to the log directory in the final failure summary transforms a "failure" into a "debugging step".
**Action:** In CLI summary reports, always calculate and display a success rate (even if 0%) and, on failure, explicitly print the path to the logs in a visually distinct style.
