# The Van Build

**Work in progress, updated 2026-10-23.** A record of converting a Ford Transit
L3H3 into a winter-capable living and working space: decisions, costs, plans,
construction and eventually what works in use.

We started writing with the wood stove. The blog covers the **whole van build**;
earlier stages will be added later. A page's writing date is not necessarily
the date the work happened. Planned work is labelled as planned, and ordered
parts are not treated as installed.

## Build Stages

- [Floor insulation: the next work](floor/index.md): remove the floor, seal
  old rivet holes, fit the stove replacement-air vent, insulate the internal
  wheel arches and finish the floor insulation.
- [Wood stove](wood_stove/index.md): the first story drafts, component choices,
  transparent costs, drawings and interactive layout planning.

**After the floor:** make the stove installation plan and gather its tools,
adhesives, fixings and remaining materials. The floor page is the current
working instruction, not a report of completed construction.

## Earlier Stages Still To Write

The earlier preparation, corrosion work, insulation decisions, windows,
roof/fan planning and electrical planning have not yet been written up as blog
chapters. Existing technical plans stay in `docs/`; they are source material,
not evidence that every planned job has been completed.

As those chapters are added, group them by build stage and record both the
work date, when known, and the writing/update date. Keep the whole-build
navigation independent of the order in which we happen to write.

## Costs And Evidence

The [stove cost ledger](wood_stove/costs.md) currently covers **stove-related
spending only**, not the whole van budget. Other stages will gain their own
cost records as they are documented. Record materials, consumables, delivery,
fees and any paid work, with estimates and unknown amounts clearly separated
from actual purchases. Unknown is not zero.

Drawings, measurements and photos belong with the relevant build stage.
Historical drawings retain their status labels; adjustable planning models
are not installation approvals.

## Reading And Maintaining The Site

Use the sun/moon control in the site header to choose **light, dark or automatic
system appearance**. The browser remembers the selection. The stove figures
can be expanded, and their original editable files downloaded. Interactive
controls run locally without uploading data or changing the source drawings.

The pages are Markdown, rendered with Sphinx and MyST. From the repository root:

```sh
uv run --no-project \
  --with-requirements docs/blog/requirements.txt \
  sphinx-build -n -W --keep-going -b html \
  docs/blog docs/blog/_build/html
python -m http.server 8000 \
  --directory docs/blog/_build/html
```

Open `http://localhost:8000`. Generated HTML stays out of Git. The editable
stove drawings stay in `docs/wood_stove/`; blog assets and tests live under
`docs/blog/`.

Geometry checks use Node's built-in test runner, with no npm dependencies:

```sh
node --test docs/blog/tests/layout-explorer.test.mjs
```

## GitHub Pages

This static site can be hosted as this repository's GitHub Pages project site,
at `https://eternalgoldenbraid.github.io/Van/` with the default domain.
The repository is public; Pages is not currently configured.

Publication requires a GitHub Actions workflow that builds `docs/blog/`,
uploads `docs/blog/_build/html` as a Pages artifact and deploys it, with
**Settings -> Pages -> Source: GitHub Actions**. Publish the generated site,
not the raw Markdown directory. Review the drafts and downloadable evidence
for public release before enabling deployment. No deployment workflow or
publication is configured by this documentation change.
