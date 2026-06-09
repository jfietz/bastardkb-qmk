## 2024-05-24 - Add ETA to build progress bar
**Learning:** For long-running batch CLI operations, users experience uncertainty regarding completion times. Adding an estimated time remaining indicator significantly improves the experience.
**Action:** Always include a TimeRemainingColumn or equivalent when implementing progress bars for batch jobs with a known total count.
