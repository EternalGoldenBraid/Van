# Project Board

Status: lightweight repo-native tracking. Keep this file short; move detailed
plans into separate `docs/` files when a task grows.

## How To Use

- `Now`: active work that is allowed to shape today's decisions.
- `Next`: queued work with enough context to start soon.
- `Later`: known work that should not distract from the current build step.
- `Done`: completed work worth keeping visible for continuity.
- Keep physical-work tasks operational: next action, blocker, and decision needed.

## Now

### Remove Diesel Heater

Goal: safely remove the existing diesel heater and leave the van in a known,
documented state before floor work continues around that area.

Next action:
- Inspect and document the heater installation before disconnecting anything.

Track:
- fuel line path and shutoff state
- electrical feed/fuse/switch/controller path
- combustion intake and exhaust penetrations
- warm-air ducting and mounting holes
- parts removed versus parts intentionally left in place
- holes that will need sealing, patching, or later reuse

Blockers / decisions:
- confirm whether the heater is being removed permanently or only temporarily
- confirm how to seal any exterior penetrations after removal

## Next

### Cargo Floor Inspection

Goal: lift the cargo floor, inspect ribs/holes/rust, and confirm the floor stack
before buying or installing the main insulation materials.

Next action:
- Lift the cargo floor, vacuum, photograph, and mark holes, rust, and factory
  drains or weep points.

Reference:
- `docs/floor_plan.md`

## Later

- Decide underfloor heating approach before permanently closing floor layers.
- Decide stove position and any through-bolted backing plates.
- Convert confirmed shopping assumptions into `scripts/material_needs_insluation.py`.

## Done

- Racks removed.
- Initial floor plan captured in `docs/floor_plan.md`.
- Initial repository pushed to GitHub.

