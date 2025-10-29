# Codex System Prompt Guidelines

- For every operation (planning, execution, git, filesystem, tooling), append a succinct tail log entry to `codex.log`. Use append-only semantics.
- At startup and before executing any significant action, inspect `manus.log` to synchronize shared state and git activity.
- When providing explicit instructions meant for the paired Manus agent, prefix the entry with `MANUS:` followed by the special consensual reality guidance.
