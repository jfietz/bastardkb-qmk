## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [CLI Build Summary]
**Learning:** In long-running CLI processes (like builds), users lose context of individual successes/failures by the end. A final summary table provides immediate, aggregated feedback, removing the need to scroll back.
**Action:** Implement a summary table (using `rich.table` if available) at the end of any batch processing CLI script.
