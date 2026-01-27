## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-10-26 - [Empty State Feedback]
**Learning:** When a user-provided filter results in zero actions (e.g., building 0 firmwares), silent success is confusing. Explicitly warning the user that their filter matched nothing prevents "did it work?" uncertainty.
**Action:** Always check for empty results after filtering and provide a clear warning or suggestion.
