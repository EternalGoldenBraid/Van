# Van Build Agent Handoff

## Current Objective

The immediate project is converting the van from cargo use toward a minimal,
winter-capable living/work setup. The current focus is the cargo floor, not the
full interior.

The build philosophy is gradual and serviceable:

- start with floor preparation and insulation
- avoid over-engineering before measurements confirm the need
- preserve the ability to revise later, especially around underfloor heating
- use simple scripts as planning aids, not as a replacement for inspecting the van

## Repository State

Important files:

- `scripts/material_needs_insluation.py`: current material and cost calculator.
- `docs/floor_plan.md`: concise current floor build plan.
- `docs/project_board.md`: lightweight current task board.

The script is intentionally rough but useful. Do not rewrite it into a framework
unless the user explicitly asks. Prefer small commits that each implement one
concept.

## Project Management

Project management is not settled. A lightweight `docs/project_board.md` exists
from an initial pass, but do not assume it is the final system.

The user created a Linear workspace/account for Brutus Van, and Codex Linear MCP
was added locally as `linear` at `https://mcp.linear.app/mcp`. A fresh Codex
session may be needed before Linear tools are available.

Current active physical task: remove the existing diesel heater and document
what remains before continuing floor work around that area.

## Floor Plan Context

Current floor stack under consideration:

1. clean cargo floor and inspect old holes/rust
2. treat holes and rust
3. optional butyl damping patches
4. 6 mm closed-cell foam
5. glued wooden battens where needed
6. 30 mm XPS infill
7. existing/owned plywood floor screwed into battens

The user is currently investigating old holes left by removed racks/rivnuts.
Measured holes are roughly 5.5-6.0 mm, with some enlarged during removal.

## Hole And Rust Treatment Decision

The current working approach:

- clean rust mechanically with wire brush/drill attachment
- degrease with IPA
- use rust converter only where rust remains in pits
- use standard metal primer
- use normal metal top coat
- close holes with rivets
- use Sikaflex 11 FC as sealant around/under rivet heads

The user considered 8 mm watertight rivets because locally available sealed
rivets in smaller sizes were difficult to find. The tradeoff is that 8 mm
requires enlarging existing 5.5-6.0 mm holes. Do not assume this is settled until
the user confirms what they bought and what hole sizes remain after cleanup.

If standard rivets are used instead of sealed rivets, the sealant bead matters:
apply a small bead around the hole, set the rivet through it, pull the rivet, and
smooth a thin bead around the rivet head.

## Current Material Notes

Recently added/updated in the material script:

- standard white primer instead of galvanized/aluminum primer
- normal white top coat instead of 3-in-1 Hammer-style paint
- brass wire brush option
- Sikaflex 11 FC for sealing rivets
- Sikaflex 118 for bonding structural floor elements
- optional rust converter and optional PU foam

Known typo in the script:

- file name is `material_needs_insluation.py` with the typo preserved from
  history.
- one note says `structural elemgents`; this can be fixed in a small cleanup
  commit.

## Commit Hygiene

The user cares about clean history. Use small semantic commits.

Preferred style:

- `insulation: ...` for script/material calculator changes
- `docs: ...` for planning documents
- one concept per commit

Do not combine behavior changes, data changes, and print-format cleanup in the
same commit unless the user explicitly asks.

## Interaction Notes

The user is actively doing physical work on the van and may be tired or making
decisions under time pressure. Keep advice operational:

- answer the immediate build decision first
- separate confirmed decisions from assumptions
- flag when a physical measurement is required
- avoid broad rewrites or heavy abstractions
