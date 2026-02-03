## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2024-05-24 - [Proactive Dependency Checks]
**Learning:** CLI tools that crash with "command not found" (or python stack traces) when external dependencies are missing feel broken. Checking for dependencies (like `qmk` or `git`) at startup and providing clear installation instructions turns a "crash" into a "setup step".
**Action:** Implement a `check_dependencies` phase at the very start of CLI entry points to validate the environment before attempting any work.
