## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2025-02-18 - [Actionable Failure Summaries]
**Learning:** A binary "success/fail" summary for batch operations leaves users digging for details. Providing a success rate percentage and an explicit file path to the logs transforms a failure message from a dead end into a clear next step.
**Action:** Enhance CLI summary panels to include actionable data (percentages, log paths) when partial failures occur, rather than just raw counts.
