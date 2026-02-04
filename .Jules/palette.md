## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2024-05-27 - [Fail Fast on Dependencies]
**Learning:** Users often assume their environment is ready. A CLI tool that runs deep before failing on a missing command (like `git` or `qmk`) causes confusion and wasted time. Checking for critical dependencies at startup and failing with a clear, instructive message is a high-value micro-UX improvement.
**Action:** Identify external command-line dependencies and add a pre-flight check using `shutil.which` at the application entry point.
