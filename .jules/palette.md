
## 2024-05-29 - [Time Remaining Indicator for Batch Operations]
**Learning:** For long-running CLI batch operations, users experience uncertainty without knowing how much time is left. Adding a time remaining indicator to progress bars significantly improves the user experience by setting clear expectations.
**Action:** When implementing global progress bars for batch tasks, include a time remaining indicator (e.g., `TimeRemainingColumn` from `rich.progress`) alongside time elapsed to reduce user anxiety.
