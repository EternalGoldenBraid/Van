# The Van Build

**Work in progress, updated 2026-10-24.** A record of converting a Ford Transit
L3H3 into a winter-capable living and working space: decisions, costs, plans,
construction and eventually what works in use.

We started writing with the wood stove. The blog covers the **whole van build**;
earlier stages will be added later. A page's writing date is not necessarily
the date the work happened. Planned work is labelled as planned, and ordered
parts are not treated as installed.

## Build Stages

- [Work-package overview](work-packages.md): a short summary of current,
  upcoming and later work, linking to instructions and shopping lists.
- [Heater removal](heater_removal/index.md): completed removal record and
  original routing photographs.
- [Diesel heater](diesel_heater/index.md): active Planar 44D relocation log,
  photos and embedded [shopping list](diesel_heater/index.md#shopping-list).
- [Floor work packages](floor/index.md):
  [rivet-hole sealing](floor/rivet_holes.md),
  [replacement-air inlet (*korvausilma*)](floor/replacement_air.md), and
  [floor levelling & XPS support](floor/levelling.md).
- [Roof fan (MaxxFan Deluxe)](maxxfan/index.md): installation flow, butyl
  levelling method, reference placeholders and embedded
  [shopping list](maxxfan/index.md#shopping-list).
- [Wood stove](wood_stove/index.md):
  [installation plan](wood_stove/installation-plan.md),
  [shopping list with costs](wood_stove/shopping_list_boutique.md), story drafts
  and the draw.io schematic.

**After the floor:** make the stove installation plan and gather its tools,
adhesives, fixings and remaining materials. The floor page is the current
working instruction, not a report of completed construction.

## Useful Places

[Useful Places](useful-places.md) is a separate, mobile-friendly reference map for places useful while operating the van, starting with two large-vehicle washes. It is not a work package. Location entries live in `_static/useful-places.json`, with the interactive map in `_static/useful-places-map.html`. The map uses OpenStreetMap and Leaflet and requires no backend API key. Avoid adding personal/home locations to the public site.

## Earlier Stages Still To Write

The earlier preparation, corrosion work, insulation decisions, windows,
roof/fan planning and electrical planning have not yet been written up as blog
chapters. Existing technical plans stay in `docs/`; they are source material,
not evidence that every planned job has been completed.

As those chapters are added, group them by build stage and record both the
work date, when known, and the writing/update date. Keep the whole-build
navigation independent of the order in which we happen to write.

## Costs And Evidence

The [stove shopping list](wood_stove/shopping_list_boutique.md) records **stove-related
spending only**, not the whole van budget. Other stages will gain their own
cost records as they are documented. Record materials, consumables, delivery,
fees and any paid work, with estimates and unknown amounts clearly separated
from actual purchases. Unknown is not zero.

Drawings, measurements and photos belong with the relevant build stage.
Historical drawings retain their status labels.

## Reading And Maintaining The Site

Use the sun/moon control in the site header to choose **light, dark or automatic
system appearance**. The browser remembers the selection. The stove's draw.io
figure opens at full size when clicked; its editable source is downloadable.

The pages are Markdown, rendered with Sphinx and MyST. From the repository root:

```sh
uv run --no-project \
  --with-requirements docs/blog/requirements.txt \
  sphinx-build -n -W --keep-going -b html \
  docs/blog docs/blog/_build/html
python3 scripts/shopping_graph.py serve --port 8000
```

Open `http://localhost:8000`. Generated HTML stays out of Git. The editable
stove drawings stay in `docs/wood_stove/`; blog pages and assets live under
`docs/blog/`.

## GitHub Pages

The GitHub Pages address is `https://eternalgoldenbraid.github.io/Van/`.
Publication makes the blog and its downloadable evidence publicly accessible.

All build documentation and blog source live on **`main`**. Use temporary
branches for drafts and merge them into `main` when ready to publish.
Work-package shopping lists are rendered from the bipartite shopping graph
(`docs/blog/_static/shopping_graph.json` and `docs/shopping_graph.sqlite`).

The workflow in `.github/workflows/blog-pages.yml` publishes relevant pushes to
**`main`**, including changes to the canonical heater shopping list. It builds
Sphinx with warnings treated as errors, uploads only
`docs/blog/_build/html` and deploys that artifact. Generated HTML stays out of
Git. Review drafts and downloadable evidence before pushing changes that
publish them.

Repository configuration uses **Settings -> Pages -> Source: GitHub Actions**.
The `github-pages` environment must allow deployments from
`main`. To retry a failed deployment, open its run under
**Actions -> Publish van-build blog** and choose **Re-run all jobs** after
fixing the cause.

If the publishing branch changes, update the workflow branch filter and the
environment's deployment rules together.
