# AGENTS.md instructions for /home/nicklas/Projects/Personal/Van

This repository is for planning and tracking the van build.

## How To Work Here

- Read `agents/handoff.md` before making planning or script changes.
- Keep the current plan in `docs/` and the executable estimates in `scripts/`.
- Treat `scripts/material_needs_insluation.py` as a practical planning script, not
  a polished package.
- Prefer small semantic commits.
- Do not combine behavior changes, material data changes, and output formatting
  cleanup in the same commit unless explicitly requested.

## Commit Prefixes

- Use `insulation: ...` for material calculator and insulation planning changes.
- Use `docs: ...` for planning notes and handoff documents.

## Current Caveat

The script filename currently contains a typo: `material_needs_insluation.py`.
Preserve it unless the user explicitly asks for a rename, because the history was
migrated with that path.

