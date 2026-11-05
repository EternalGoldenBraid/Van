# Shopping & Work-Package Graph

Filter shopping items by **work package** (click a pill above or a work-package
node on the left) and by **status** (`All`, `To buy`, `Ordered`, `Owned`).

You can also **change an item's status** using its dropdown in the table, **add
new items** (`+ Add item`), or **remove items** (`✕`):

- **On `localhost:8000`** (`python3 scripts/shopping_graph.py serve`): edits
  save directly to `docs/blog/_static/shopping_graph.json` and
  `docs/shopping_graph.sqlite`.
- **On GitHub Pages:** click **GitHub Sync** once to store a GitHub Personal
  Access Token in your browser (`localStorage`), and edits commit straight to
  `EternalGoldenBraid/Van`.

```{raw} html
<div class="js-shopping-graph" data-graph-url="_static/shopping_graph.json">
  <p>Loading interactive bipartite graph…</p>
</div>
```

## Prices

The graph now stores an optional **listed unit or pack price in euros** for each
shopping item. Click an item, then open **Edit details & work packages** to
set its price. A dash means the price is not verified yet; it is not zero.
Listed prices are not necessarily the amounts paid. Shared tools appear in
multiple work packages but represent a single purchase, not repeated costs.

## Updating From Terminal

```bash
python3 scripts/shopping_graph.py set-status 10129724 ordered --date 2026-10-26
python3 scripts/shopping_graph.py add --name "Sikaflex-221" --packages maxxfan --status planned
python3 scripts/shopping_graph.py remove item:sikaflex_221
```

