## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2024-05-27 - [Dependency Pre-flight Checks]
**Learning:** CLI tools that rely on external binaries (like `git`, `qmk`) often fail with cryptic tracebacks deep in execution when these are missing. Adding explicit, early checks for these dependencies prevents user confusion and saves time.
**Action:** Always check for critical external dependencies at the start of a CLI tool's execution and provide clear instructions if they are missing.
