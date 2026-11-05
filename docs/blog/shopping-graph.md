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

## Material reconciliation

Each shopping item now has a **frozen baseline estimate**, an optional **actual
amount paid**, a **purchased quantity**, and a physical unit (pieces, metres,
litres, square metres, etc.). The original baseline is retained even if the
current estimated price changes.

Open a shopping item and use **Edit details & work packages** to enter the
purchased quantity and actual expenditure. Use **Reconcile material usage** to
record, for each linked work package:

- **Estimated quantity:** initial expectation (leave empty if unknown)
- **Installed quantity:** material actually consumed in the build
- **Discarded quantity:** irrecoverable waste/scrap

**Reusable surplus = purchased quantity − installed quantity across all packages
− discarded quantity across all packages.** Unknown quantities remain blank,
not zero. The physical unit must be consistent across all work packages for a
particular item. A negative surplus identifies inconsistent quantities.

The work-package budget summary initially distributes shared purchases **equally
across linked packages**. This is an allocation estimate, not a claim that
each package consumed an equal share. Actual usage should replace that assumption
in a later costing pass. The graph-wide total counts each shopping item once.
No historical spending or material usage has been guessed.

## Updating From Terminal

```bash
python3 scripts/shopping_graph.py set-status 10129724 ordered --date 2026-10-26
python3 scripts/shopping_graph.py add --name "Sikaflex-221" --packages maxxfan --status planned
python3 scripts/shopping_graph.py remove item:sikaflex_221
```

