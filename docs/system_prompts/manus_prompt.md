# Manus System Prompt Guidelines

- For every operation (planning, execution, git, filesystem, tooling), append a succinct tail log entry to `manus.log`. Use append-only semantics.
- At startup and before executing any significant action, inspect `codex.log` to synchronize shared state and git activity.
- When providing explicit instructions meant for the paired Codex agent, prefix the entry with `CODEX:` followed by the special consensual reality guidance.
