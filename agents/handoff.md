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

The script is intentionally rough but useful. Do not rewrite it into a framework
unless the user explicitly asks. Prefer small commits that each implement one
concept.

## Project Management

Linear is the active task board. The old repo-native `docs/project_board.md`
was removed after the current work was migrated into the `Van Build` Linear
project.

Project URL:
- `https://linear.app/brutusvan/project/van-build-45e37d1faceb`

The user created a Linear workspace/account for Brutus Van, and Codex Linear MCP
was added locally as `linear` at `https://mcp.linear.app/mcp`. A fresh Codex
session may be needed before Linear tools are available.

Current active physical task (2026-10-06): prepare and seal remaining old
pop-rivet floor holes before permanent floor installation. See
[`docs/floor_sealing_logbook.md`](../docs/floor_sealing_logbook.md).

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

The current chosen approach (2026-10-06) supersedes the earlier rivet plan:

- inside bolt -> washer -> bike-inner-tube rubber seal -> van floor ->
  rubber seal -> washer -> outside nut
- mechanically remove loose rust, clean, and dry both faces and hole edges
- the user owns CRC Rust Seal 750 ml; its retailer says it also protects without
  paint, so a separate primer is not assumed mandatory over the converter
- confirm application/cure instructions before clamping the seals and check
  leak-tightness before covering the floor
- Rostex Super Akva is recommended, not purchased, for fresh bare-steel cut
  edges; it requires a compatible water-based topcoat, not an assumed Maston
  spray finish

The floor remains blocked by these holes. Underbody treatment is now expected
in about a month; the exact appointment needs reconfirmation. See the linked
logbook for product sources, coating limitations, and next actions.

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
