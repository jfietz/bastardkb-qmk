## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2024-05-24 - [Dry Run Transparency]
**Learning:** CLI tools that report success in dry-run mode without visual differentiation can confuse users into thinking artifacts were created. Explicitly marking "Dry Run" in the final summary (e.g., using a distinct color like blue) aligns system status with user expectations.
**Action:** When implementing dry-run modes, always modify the success/failure messaging and styling to clearly distinguish it from a live execution.
