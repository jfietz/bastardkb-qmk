
## 2024-06-11 - Add Estimated Time Remaining for Progress Bars
**Learning:** For long-running CLI batch operations, users experience less uncertainty and better UX when provided with an estimated time remaining indicator alongside the elapsed time and completion percentage.
**Action:** Always include a `TimeRemainingColumn` or equivalent ETA indicator when implementing global progress bars for long-running batch operations.
