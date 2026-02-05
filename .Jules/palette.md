## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2024-05-25 - [Proactive Dependency Checks]
**Learning:** CLI tools that rely on external binaries (like `qmk` or `git`) fail obscurely when those tools are missing. Implementing a startup check using `shutil.which` allows for friendly, instructional error messages instead of cryptic stack traces.
**Action:** Identify all external CLI dependencies and implement a "pre-flight check" that validates their presence before attempting execution.
