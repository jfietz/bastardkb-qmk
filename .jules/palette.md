## 2024-06-12 - Added TimeRemainingColumn to global progress bar
**Learning:** For long-running CLI batch operations using rich.progress, users experience less uncertainty and better UX when an estimated time remaining indicator (e.g., TimeRemainingColumn) is included in the global progress bar, in addition to TimeElapsedColumn.
**Action:** When setting up global progress bars for long-running batches (like building many firmwares), add TimeRemainingColumn to the Progress object initialization to provide ETA feedback to the user.
