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

Use the sun/moon control in the site header to choose **light or dark
appearance**. The browser remembers the selection. The stove's draw.io
figure opens at full size when clicked; its editable source is downloadable.

All published pages are Markdown rendered with VitePress. Node.js 20+ is
required; the local shopping API also uses Python 3.10+ and the existing graph
synchronizer. From the repository root:

```sh
npm --prefix docs/blog ci
npm --prefix docs/blog run dev
```

Open `http://127.0.0.1:8766`. Source edits hot-reload directly. Generated HTML
and caches stay under `docs/blog/_build/`, outside Git. The editable
stove drawings stay in `docs/wood_stove/`; blog pages and assets live under
`docs/blog/`.

The shopping graph uses the existing JSON and SQLite mirror. Local browser
edits save to those real repository files, without a commit or push; reading
alone does not rewrite them. If the local shopping API is unavailable,
editing is disabled. Local previews never fall back to GitHub Sync.

Build and check all published pages and the graph adapter:

```sh
npm --prefix docs/blog test
```

Site navigation, search and the deployment base live in `.vitepress/config.mjs`.
Use native Markdown, `::: info` blocks and `<!--@include: ./file.md-->`
includes. `README.md` files are included source/reference documents, not
separate published pages. Downloads use the theme's `$withBase` helper.
`public/` links to canonical assets and selected planning-file downloads;
legacy Sphinx download aliases preserve existing public URLs. Keep these
links pointed at their original sources, without duplicating editable content.

### Local Agent Comments

Comments are optional and use the separate `agent-doc-review` checkout.
No comment service or connection data is included in the published site.

Connect a session-scoped Copilot extension using the
`agent-doc-review/docs/preview-comments.md` adapter instructions. Set its
`documentRoot` to this repository's `docs/blog`, `previewOrigin` to
`http://127.0.0.1:8766`, and `storageRoot` to a private local directory outside
Git. Reload the extension, then use its logged connection-file path:

```sh
node scripts/blog_review.mjs \
  --review-package /absolute/path/to/agent-doc-review \
  --connection-file /absolute/private/state/session-id/connection.json
```

Open `http://127.0.0.1:8766/`. Select text and click **Comment**;
**History** shows replies and resolution. Feedback stays in the owning Copilot
session's local state. Do not share or commit the connection file or comments.
If changing `--port`, change the extension's preview origin to match.

Comments map to the original Markdown under `docs/blog/`. Saved comments remain
in the private state directory when the server stops. The review plugin is
loaded only for this local command; VitePress itself is pinned in this blog's
package manifest and lockfile.

## GitHub Pages

The GitHub Pages address is `https://eternalgoldenbraid.github.io/Van/`.
Publication makes the blog and its downloadable evidence publicly accessible.

All build documentation and blog source live on **`main`**. Use temporary
branches for drafts and merge them into `main` when ready to publish.
Work-package shopping lists are rendered from the bipartite shopping graph
(`docs/blog/_static/shopping_graph.json` and `docs/shopping_graph.sqlite`).

The workflow in `.github/workflows/blog-pages.yml` publishes relevant pushes to
**`main`**, including changes to the canonical heater shopping list. It builds
VitePress with dead-link checking and runs the graph/site checks, uploads only
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
