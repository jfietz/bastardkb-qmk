
## 2024-05-29 - [Progress Bar ETA]
**Learning:** For long-running batch processes, a simple progress bar (M of N) and elapsed time is often not enough. Users experience anxiety about how much longer the process will take. Adding an estimated time of arrival (ETA) or time remaining column reduces uncertainty and makes the wait feel shorter.
**Action:** When using `rich.progress` for batch operations, always include `TimeRemainingColumn` alongside `TimeElapsedColumn` to provide a complete picture of the process's duration.
