# Concise Work Logbooks

Write a technical handoff that lets the next person resume without reading
the conversation. Keep topic notes in `docs/`; this is not a new task board.
Persistent agent/session coordination stays in `agents/roster.md`.

## Writing Rules

- Lead with the current decision and its status: confirmed, provisional, or
  blocked. Never turn a preference into a purchase or completed installation.
- Put the update date, client, and known resumable session ID at the top.
  If the ID is unavailable, say so; do not invent one.
- Aim for one screen of main content, roughly 200-400 words excluding links.
  Keep necessary safety constraints even if that requires a little more.
- Separate verified facts, manufacturer claims, observed examples, and unknowns.
  Retain units and the exact model/system to which dimensions apply.
- Link directly to sources, instructions, and relevant video timestamps.
  Link to existing plans rather than duplicating them.
- State what remains unresolved and the smallest concrete next action.
- Update the current summary in place. Keep only earlier decisions or negative
  findings that prevent repeating work; omit transcripts and search narration.
- Read the existing note and `agents/handoff.md` before editing. Confirm write
  targets, respect other agents' changes, and do not create duplicate records.

## Template

```markdown
# <Topic> Logbook

**Session (<client>):** `<session ID or unavailable>`
**Updated:** YYYY-MM-DD
**Status:** <current decision and whether it is provisional/blocked/complete>

## Current Direction
<Chosen approach, one-line rationale, and essential constraints.>

## Findings And Sources
<A few linked facts. Label claims, observations, and uncertainty.>

## Open / Next
<Unresolved decisions, required measurements, and next concrete action.>
```

Add a short safety or earlier-evidence section only when it changes what the
next person may safely assume or do. The stove example is
[blog/wood_stove/research.md](blog/wood_stove/research.md).
