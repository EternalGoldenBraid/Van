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

Copilot CLI and Codex store session files locally on the machine where the
session ran (`~/.copilot/session-state/<id>` and `~/.codex/sessions/`). A
session ID can only be resumed on the machine that holds its local state (unless
copied over); on another machine, start a named session (e.g.
`copilot --name wood-stove`) and point it at the territory's handoff docs.

| Agent | Territory | Client / Linear | Machine | Worktree | Resume / Start |
| --- | --- | --- | --- | --- | --- |
| Wood stove research & chimney sourcing | `docs/blog/wood_stove/` (installation, research, shopping list with costs, story drafts) | Copilot CLI | Laptop & Desktop | `/home/nicklas/Projects/Van` | `copilot --resume e190de56-148f-44f3-adc6-c8c9129359be` |
| Wood stove diagrams | `docs/wood_stove/boutique-chimney-plan.{drawio,excalidraw}` | Codex | Desktop (`gitnicklas@pm.me`) | `/home/nicklas/Projects/Van` | `codex resume 01a14f95-1070-76a1-8f77-e63c4bc7ac8b -C /home/nicklas/Projects/Van` |
| Floor sealing & cut-edge protection | `docs/floor_sealing_logbook.md`, `docs/floor_plan.md` | Copilot CLI | Laptop (`nestai.com`) | `/home/nicklas/Projects/Van` | On laptop: `copilot --resume 7d21c491-efb2-4df8-90bc-f5c31d6ea54f`<br>On desktop: `copilot --name floor-sealing` (read `docs/floor_sealing_logbook.md`) |
| Blog dashboard & diesel heater docs | `docs/blog/index.md`, `docs/blog/diesel_heater/`, `docs/diesel_heater/shopping_list.md` | Copilot CLI | Desktop (`gitnicklas@pm.me`) | `/home/nicklas/Projects/Van` (`main`) | `copilot --resume 78934608-4dae-4eff-8ad0-2f71547ae5ae` |
| Main Codex session | Project coordination, Linear tracking, repo hygiene, physical-work planning | Codex / General | Laptop (`/Personal/Van/main`) | `/home/nicklas/Projects/Personal/Van/main` | `codex resume 019e7848-8459-7100-bf9f-10fa969a9bf3 -C /home/nicklas/Projects/Personal/Van/main` |
| Electronics wiring diagram agent | Maintain `docs/electronics_wiring.drawio`, starting with the heater path | Codex / `VAN-23` child of `VAN-22` | Laptop (`/Personal/Van/...`) | `/home/nicklas/Projects/Personal/Van/van-23-heater-wiring` | `codex resume 019e79a5-c112-7373-8fdd-a535f34446f7 -C /home/nicklas/Projects/Personal/Van/van-23-heater-wiring` |

## Notes

- Record all resumable agent/session IDs here in `agents/roster.md` rather than
  inside public blog pages under `docs/blog/`.
- When a new persistent agent starts, it should check this roster. If it is not
  listed yet, it should add its own entry with territory, Linear issue, worktree,
  branch, session/thread ID, and resume command.
- A user-managed agent should be able to start from its worktree and assigned
  Linear issue. The first prompt can be as small as: "Check your assigned issue
  and get the context."
- The project context comes from the `Van Build` Linear project, not from a
  repo-native task board.
- The transient in-thread worker that created the first wiring diagram
  draft was not a persistent CLI session.
- For new persistent agents, create a named worktree and add its resume command
  here before relying on it after reboot.
- Do not store secrets, API keys, or private credentials in this file.

## Documentation Style for All Agents

Treat the repository as the **distilled current state of the build**, not a transcript or a general-purpose installation manual.

- **High information density:** preserve measurements, installed parts, decisions, purchase status, useful photos, links and genuine open questions.
- **Avoid clutter:** omit obvious reminders, repeated general safety warnings, boilerplate disclaimers and hypothetical alternatives that do not affect the actual build.
- **Separate facts from plans:** clearly distinguish installed, measured, proposed, ordered and unverified details; do not invent confirmation.
- **Shopping lists should be actionable:** prioritize items actually needed, direct product links, quantities, and purchase status; keep irrelevant candidates out.
- **Review before writing:** propose selective documentation updates at meaningful milestones rather than automatically committing every conversational decision.
- Preserve specific, material safety constraints where they change a design or action; avoid turning notes into exhaustive generic guidance.

These conventions apply to every agent editing project documentation.
