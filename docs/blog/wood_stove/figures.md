# Figures And Editable Drawings

These drawings are part of the build record, not just links to attachments.
Expand a figure to inspect its labels; download its original to edit locally.
The [layout explorer](layout.md) is a separate, live geometric model:
its controls do not rewrite these files.

**Historical schematics, not construction drawings.** The original draw.io
purchase badges and flashing comparison predate the latest orders. Excalidraw
is an earlier concept. Use the [shopping list](shopping_list_boutique.md)
and [cost ledger](costs.md) for current purchases and amounts.

## Draw.io: Assembly And Roof Passage

```{figure} ../_static/figures/chimney-drawio.png
:name: fig-chimney-drawio
:alt: Draw.io side elevation showing the stove, single-wall flue, connector, insulated chimney, roof weather seal and separate structural support, with notes about unresolved heights.

Assembly schematic and sourcing notes, last edited 2026-10-20.
Not to scale; mounting and clearance dimensions remain unresolved.
```

{download}`Download editable draw.io source <../../wood_stove/boutique-chimney-plan.drawio>`.
Open it in the draw.io desktop app or the VS Code draw.io extension.

## Excalidraw: Earlier Concept

```{figure} ../_static/figures/chimney-excalidraw.png
:name: fig-chimney-excalidraw
:alt: Earlier Excalidraw concept identifying outlet-to-terminal rise, projection above the roof and stove mounting elevation alongside a symbolic chimney assembly.

Earlier side-view concept. The three height questions remain useful, but its
candidate parts and before-ordering notes are historical.
```

{download}`Download editable Excalidraw source <../../wood_stove/boutique-chimney-plan.excalidraw>`.
Open/import the file in Excalidraw. Editing or publishing through a hosted
service is not required by this site.

## Keeping Figures Current

The editable files remain the source drawings. After an edit, regenerate the
corresponding preview and inspect it before updating the site. Do not infer
physical dimensions from either schematic's pixel coordinates.

The draw.io preview is a CLI export of the `.drawio` source in
`docs/wood_stove/`.
The Excalidraw preview is cropped from the existing rendered scene with the
editor controls removed; the matching original scene is preserved unchanged.

To refresh draw.io's preview from the repository root:

```sh
drawio --export --format png \
  --output docs/blog/_static/figures/chimney-drawio.png \
  docs/wood_stove/boutique-chimney-plan.drawio
```

For an edited Excalidraw scene, export a PNG without editor controls to
`docs/blog/_static/figures/chimney-excalidraw.png`. Keep the updated
editable scene in `docs/wood_stove/`, then rebuild and inspect the site.
