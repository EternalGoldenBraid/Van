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
- `docs/blog/README.md`: whole-van blog, build-stage navigation and preview
  instructions. Stove stories are one section; earlier stages remain to write.

The script is intentionally rough but useful. Do not rewrite it into a framework
unless the user explicitly asks. Prefer small commits that each implement one
concept.

Build documentation and the blog share `main`. Use temporary branches for drafts;
relevant pushes to `main` publish the blog. The canonical diesel-heater shopping
list is `docs/diesel_heater/shopping_list.md`, included directly by its blog page.

## Project Management

Linear is the active task board. The old repo-native `docs/project_board.md`
was removed after the current work was migrated into the `Van Build` Linear
project.

Project URL:
- `https://linear.app/brutusvan/project/van-build-45e37d1faceb`

The user created a Linear workspace/account for Brutus Van, and Codex Linear MCP
was added locally as `linear` at `https://mcp.linear.app/mcp`. A fresh Codex
session may be needed before Linear tools are available.

Current tooling note:

- GitHub Copilot CLI in this environment does not currently expose the Linear
  MCP setup, so do not rely on stale session memory for Linear-backed facts.
- If fresh Linear issue data or photos are needed, resume this thread in Codex
  and use the live Linear MCP there.

Current physical work sequence (2026-10-23): remove the floor, seal old rivet
holes using the [existing plan](../docs/floor_sealing_logbook.md), fit the stove
replacement-air vent, apply closed-cell foam to the internal wheel arches,
then finish the floor insulation. The
[floor working chapter](../docs/blog/floor/index.md) is the current instruction;
stove installation planning and gathering tools/materials follow.

## Electrical Planning Handoff For Codex

Current planning artifacts:

- `scripts/material_needs_electronics.py`: Victron-leaning 12V shopping list
  based on Suomen Akut pricing, with optional shore/solar/upgrade/tooling
  sections.
- `docs/electronics_victron_12v.drawio`: current planning diagram showing the
  unresolved old auxiliary path and the proposed new 12V subsystem.

Current electrical conclusions:

- Recommended baseline remains a new independent **12V** house subsystem, not
  24V or 48V.
- The proposed positive-side structure is:
  battery -> main fuse -> main switch -> positive distribution
  (`Victron Lynx Distributor` in the current plan).
- The proposed negative-side structure is:
  battery negative -> `SmartShunt` -> negative busbar -> all negative returns.
- The user now understands the role split between:
  - main battery fuse
  - Lynx branch fuses
  - small-load fuse block fuses
  - SmartShunt as measurement only, not protection
- The inverter is treated as a future DC load with:
  - positive feed from the positive distribution/Lynx branch
  - negative return after the SmartShunt via the negative busbar
- The Lynx Distributor is understood as a convenience/integration choice, not a
  hard requirement. A busbar + separate fuse holders is still a valid fallback.

Current alternator / old auxiliary open question:

- There is an existing old auxiliary battery/system that appears to have some
  alternator-linked charging path and existing inverters attached.
- Repo/session history previously identified observed relay hardware near the
  passenger-seat battery area as:
  - `3 x Wehrle 20 210 100A`
  - `Wurth 734 12 2` sockets
- That hardware alone still does **not** prove the full old charging topology.
- The current working rule remains:
  **do not tie the old auxiliary battery directly to the new house bank.**
- It may be possible to leave the old aux system in place temporarily while
  adding a new DC-DC charger branch for the new house system, but only after
  the old path is traced and the alternator-side load is understood.

What Codex should do next:

1. Use live Linear MCP to inspect the latest issue context, images, and any
   notes related to the existing auxiliary battery / relay / alternator setup.
2. Identify whether the old system is using a split-charge relay, VSR,
   combiner, DC-DC charger, or something else.
3. Determine whether the new DC-DC charger can safely coexist in parallel from
   the starter/alternator side while the old aux system remains in place.
4. After that, move into sizing work for:
   - branch currents
   - fuse ratings
   - cable cross-sections
   - cable lengths once the user measures real routing distances on-van

Known practical limitation:

- Cable runs are not yet measured on the van, so final cable gauge and fuse
  recommendations are still blocked on physical measurement.

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
- Rostex Super Akva and Panssari Akva are selected, not purchased, as the
  shared brush-on system for fresh bare-steel cut edges. The topcoat colour
  target is RAL 9010; quantities and stock/tint checks live in
  `docs/diesel_heater/shopping_list.md`.

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
