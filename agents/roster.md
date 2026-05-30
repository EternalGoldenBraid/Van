# Agent Roster

This file tracks active or reusable agents for the van build. Keep it simple:
agent territory, linked Linear issue, working tree, and resume command. Do not
list planned agents before they are actually launched.

## Workspace Layout

Preferred layout after the worktree migration:

- `/home/nicklas/Projects/Personal/Van/` is a parent coordination directory,
  not a Git repo.
- `/home/nicklas/Projects/Personal/Van/main/` is the main checkout.
- `/home/nicklas/Projects/Personal/Van/<task-worktree>/` are sibling Git
  worktrees for bounded agent tasks.

Use one branch per task, preferably matching the issue name without extra
service-specific prefixes.

## Enrolled Agents

| Agent | Territory | Linear | Worktree | Resume |
| --- | --- | --- | --- | --- |
| Main Codex session | Project coordination, Linear tracking, repo hygiene, physical-work planning | General / current thread | `/home/nicklas/Projects/Personal/Van/main` | `codex resume 019e7848-8459-7100-bf9f-10fa969a9bf3 -C /home/nicklas/Projects/Personal/Van/main` |
| Electronics wiring diagram agent | Maintain `docs/electronics_wiring.drawio`, starting with the heater path | `VAN-23` child of `VAN-22` | `/home/nicklas/Projects/Personal/Van/van-23-heater-wiring` on branch `van-23-heater-wiring` | `codex resume 019e79a5-c112-7373-8fdd-a535f34446f7 -C /home/nicklas/Projects/Personal/Van/van-23-heater-wiring` |

## Notes

- When a new persistent agent starts, it should check this roster. If it is not
  listed yet, it should add its own entry with territory, Linear issue, worktree,
  branch, session/thread ID, and resume command.
- A user-managed agent should be able to start from its worktree and assigned
  Linear issue. The first prompt can be as small as: "Check your assigned issue
  and get the context."
- The transient in-thread worker that created the first wiring diagram
  draft was not a persistent CLI session.
- For new persistent agents, create a named worktree and add its resume command
  here before relying on it after reboot.
- Do not store secrets, API keys, or private credentials in this file.
