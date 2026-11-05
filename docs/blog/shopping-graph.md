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

The graph records a **EUR budget per shopping entry**. Entries with `≈`
are estimates; other amounts are retailer-listed figures. Prices for a specified
number of sheets or rolls include that quantity when noted in the item details.
For items marked *as needed*, a provisional quantity is assumed. Click an item,
then open **Edit details & work packages** to override its price.

The summary shows a total for the current filter, counting shared tools once
within that view. **Do not sum work-package totals**: the same tool may be linked
to multiple packages. Prices are not receipts and the total can contain already
owned tools, optional materials and unpurchased estimates. Some reused items are
set to €0 incremental cost, not zero historical value.

## Updating From Terminal

```bash
python3 scripts/shopping_graph.py set-status 10129724 ordered --date 2026-10-26
python3 scripts/shopping_graph.py add --name "Sikaflex-221" --packages maxxfan --status planned
python3 scripts/shopping_graph.py remove item:sikaflex_221
```

