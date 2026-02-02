## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2024-10-24 - [Proactive Dependency Checks]
**Learning:** CLI tools that wrap external commands often fail with obscure `FileNotFoundError` tracebacks when those commands are missing. Explicitly checking for dependencies at startup and reporting missing ones with clear instructions builds trust and guides the user to a solution faster.
**Action:** Identify external command dependencies in scripts and implement a "pre-flight check" that validates their presence before attempting execution.
