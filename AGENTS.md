# AGENTS.md instructions for /home/nicklas/Projects/Personal/Van/main

This repository is for planning and tracking the van build.

## How To Work Here

- Read `agents/handoff.md` before making planning or script changes.
- Check `agents/roster.md` when resuming or coordinating active Codex agents.
- Keep the current plan in `docs/` and the executable estimates in `scripts/`.
- Treat `scripts/material_needs_insluation.py` as a practical planning script, not
  a polished package.
- Prefer small semantic commits.
- Do not combine behavior changes, material data changes, and output formatting
  cleanup in the same commit unless explicitly requested.

## Collaboration Boundaries

- Discuss project-management structure and tool choices before creating or
  changing the system of record.
- Keep persistent agent/session coordination in `agents/roster.md`.
- Do not spawn or resume sub-agents unless the user explicitly asks for that.
  Preparing a worktree or documenting an agent slot is fine; starting the agent
  is user-controlled unless delegated explicitly.
- Do not create Linear comments, change issue status, or otherwise write to
  Linear unless the user explicitly asks for that specific write. Draft review
  notes in chat first so the user can approve or edit them.
- Do not commit or push changes unless the user explicitly asks for that.
- When exploring external tools such as Linear, start with read-only checks and
  confirm before creating or updating real tasks.

## Commit Prefixes

- Use `insulation: ...` for material calculator and insulation planning changes.
- Use `docs: ...` for planning notes and handoff documents.

## Current Caveat

The script filename currently contains a typo: `material_needs_insluation.py`.
Preserve it unless the user explicitly asks for a rename, because the history was
migrated with that path.
