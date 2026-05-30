# Agent Roster

This file tracks active or reusable agents for the van build. Keep it simple:
agent territory, linked Linear issue, working tree, and resume command.

## Workspace Layout

Preferred layout after the worktree migration:

- `/home/nicklas/Projects/Personal/Van/` is a parent coordination directory,
  not a Git repo.
- `/home/nicklas/Projects/Personal/Van/main/` is the main checkout.
- `/home/nicklas/Projects/Personal/Van/<task-worktree>/` are sibling Git
  worktrees for bounded agent tasks.

Use one branch per task, preferably matching the Linear issue.

## Enrolled Agents

| Agent | Territory | Linear | Worktree | Resume |
| --- | --- | --- | --- | --- |
| Main Codex session | Project coordination, Linear tracking, repo hygiene, physical-work planning | General / current thread | `/home/nicklas/Projects/Personal/Van/main` | `codex resume 019e7848-8459-7100-bf9f-10fa969a9bf3 -C /home/nicklas/Projects/Personal/Van/main` |
| Heater documentation agent | Document the diesel heater model, manual, install state, penetrations, wiring, fuel path, and removal notes | `VAN-6` | existing external/session agent | Resume command not recorded yet |
| Heater wiring diagram agent | Maintain `docs/heater_wiring.drawio` and trace heater-to-battery wiring from evidence | `VAN-23` | planned: `/home/nicklas/Projects/Personal/Van/van-23-heater-wiring` | Not started yet |

## Notes

- The transient in-thread worker that created the first `docs/heater_wiring.drawio`
  draft was not a persistent CLI session.
- For new persistent agents, create a named worktree and add its resume command
  here before relying on it after reboot.
- Do not store secrets, API keys, or private credentials in this file.
