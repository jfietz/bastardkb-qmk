## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-10-24 - [Status Iconography]
**Learning:** Using clear icons (✔, ✘, ⚠) alongside text status messages dramatically improves scanability in CLI output compared to text-only "ok/ko".
**Action:** Replace text-based status codes with standard Unicode icons and color coding in CLI tools using `rich`.
