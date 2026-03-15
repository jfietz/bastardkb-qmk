## 2024-05-22 - [CLI Error Visibility]
**Learning:** CLI tools often bury critical configuration errors in plain text logs. Using visual containers like `rich.panel` for fatal errors transforms them from "noise" to "actionable blockers", significantly reducing user frustration during setup.
**Action:** Always check if a CLI tool has a "rich" output library available and use it to style fatal errors with distinct borders and colors.

## 2024-05-24 - [Smart Defaults in CLI]
**Learning:** Build tools that default to single-threaded execution on modern hardware create a sluggish first impression. Auto-detecting resources (like `os.cpu_count()`) respects the user's hardware and time, making the tool feel "smart" out of the box.
**Action:** Inspect CLI default arguments for performance bottlenecks and replace static defaults with dynamic, environment-aware values where safe.

## 2024-05-25 - [Respectful Logging]
**Learning:** Cluttering the user's current working directory with log files creates friction and requires cleanup. Users expect tools to be "tidy" by default.
**Action:** Use standard state directories (like XDG_STATE_HOME) for logs and only surface the location when necessary (e.g., on failure or in summary).

## 2024-05-26 - [Batch Operation Error Visibility]
**Learning:** UX guidelines for CLI tools dictate that batch operations should aggregate and list specific failed items in the final summary output to prevent users from having to scroll up through extensive logs.
**Action:** When a batch process has failures, always list the failed item names (e.g. firmwares) in the final summary.

## 2024-05-27 - [Missing Dependency Error Visibility]
**Learning:** Checking for necessary external dependencies (like `git` and `qmk`) proactively and displaying a nicely formatted `reporter.fatal()` message telling the user to install them and add them to their PATH is a significant UX improvement over simply failing with a Python `FileNotFoundError` stack trace during execution.
**Action:** Validate critical external CLI command dependencies at script startup and handle missing tools gracefully using styled panels instead of raw stack traces.

## 2024-05-15 - Visual Distinction for Simulated Outputs
**Learning:** Users experience cognitive dissonance when a dry-run or simulated process reports as "built" or "failed" with the same visual styling (green/red) as an actual execution. Missing artifacts in a dry run are expected, not failures.
**Action:** Always provide clear visual distinction (e.g., "simulated" text, blue coloring) for simulated or dry-run states to differentiate them from actual persistent actions.

## 2024-05-28 - [CLI Help Without Dependencies]
**Learning:** For CLI tools written in Python, placing third-party imports in an unconditional block prevents users from even reading the `--help` menu before running `pip install`. This is an unexpected friction point, especially for users just exploring the tool.
**Action:** Wrap third-party dependencies in a `try...except ImportError` block that allows the `argparse` help text to execute successfully when `-h` or `--help` is invoked, only re-raising the import error if the tool is invoked to actually run. Include `from __future__ import annotations` to ensure types like `Optional[Sequence[Firmware]]` are deferred.
