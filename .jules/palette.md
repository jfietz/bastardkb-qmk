## 2026-06-13 - Add TimeRemainingColumn to CLI progress bar
**Learning:** Adding a time remaining estimate to long-running CLI batch operations significantly improves the user experience by reducing uncertainty and giving users better visibility into process completion.
**Action:** Always include an estimated time remaining indicator (like `TimeRemainingColumn` in `rich.progress`) in global progress bars for potentially lengthy background or batch operations.
