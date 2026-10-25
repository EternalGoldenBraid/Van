# Chimney Figure

Draw.io schematic of the selected assembly and roof passage. Click the image
to open it at full size, or download the editable source.

**Historical schematic, last edited 2026-10-20.** Purchase badges and flashing
comparisons predate the latest orders. Use the
[shopping list](shopping_list_boutique.md) for current parts and costs and the
[installation process](installation-plan.md) for the work sequence.

```{figure} ../_static/figures/chimney-drawio.png
:name: fig-chimney-drawio
:alt: Draw.io side elevation showing the stove, single-wall flue, connector, insulated chimney, roof weather seal and separate structural support.

Assembly and roof-passage schematic. Not to scale; final mounting and
clearance dimensions remain unresolved.
```

{download}`Download editable draw.io source <../../wood_stove/boutique-chimney-plan.drawio>`.
Open it in the draw.io desktop app or the VS Code draw.io extension.

## Updating The Figure

Keep the editable source in `docs/wood_stove/`. Export its preview from the
repository root:

```sh
drawio --export --format png \
  --output docs/blog/_static/figures/chimney-drawio.png \
  docs/wood_stove/boutique-chimney-plan.drawio
```

Rebuild and inspect the rendered figure after an edit.
