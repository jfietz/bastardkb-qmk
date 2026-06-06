## 2024-06-06 - Add estimated time remaining to global progress bar
**Learning:** For long-running CLI batch operations, users often experience uncertainty. Including an estimated time remaining indicator significantly improves user experience by setting clear expectations.
**Action:** Use `TimeRemainingColumn` in `rich.progress` to display the estimated completion time.
