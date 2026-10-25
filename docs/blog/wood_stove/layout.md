---
hide-toc: true
---

# Interactive Layout Explorer

Compare stove placement in **plan view and side elevation**. Change the inputs
to update both drawings and the derived height budget. Nothing is ordered,
saved to the source drawings or uploaded by these controls.

**Planning geometry only.** Clearances, roof cutout, deployed leg dimensions,
flue outlet offset, connector seating, cap height, doors, wheel arches, rack,
fan and furniture are not modelled. A box fitting inside this sketch does not
establish a safe or buildable installation.

```{raw} html
<section class="layout-explorer" aria-label="Interactive stove layout">
  <noscript>This explorer needs JavaScript. The figures and technical notes remain available without it.</noscript>
  <form id="stove-layout-form">
    <fieldset>
      <legend>Stove and placement</legend>
      <div class="layout-input-grid">
        <label>Stove envelope<select name="preset"><option value="boutique">Boutique Traditional (placeholder)</option><option value="custom">Custom dimensions</option></select></label>
        <label>Mounting elevation (mm)<input name="mountHeight" type="number" min="0" max="1000" step="1" value="0" required></label>
        <label>Vehicle side<select name="side"><option value="driver">Driver / left</option><option value="passenger">Passenger / right</option></select></label>
        <label>Door direction<select name="orientation"><option value="aisle">Toward aisle</option><option value="rear">Toward rear doors</option><option value="cab">Toward cab</option></select></label>
        <label>Centre from front of load bay (mm)<input name="position" type="number" min="0" max="5000" step="1" value="750" required></label>
        <label>Body edge from selected wall (mm)<input name="wallGap" type="number" min="0" max="1500" step="1" value="150" required></label>
      </div>
      <p id="stove-dimension-note" class="layout-note"></p>
      <details id="stove-size-details">
        <summary>Edit stove dimensions</summary>
        <div class="layout-input-grid">
          <label>Body width (mm)<input name="stoveWidth" type="number" min="100" max="1000" step="1" value="445" required></label>
          <label>Body depth (mm)<input name="stoveDepth" type="number" min="100" max="1000" step="1" value="285" required></label>
          <label>Body/leg height (mm)<input name="stoveHeight" type="number" min="100" max="1500" step="1" value="323" required></label>
        </div>
      </details>
    </fieldset>
    <fieldset>
      <legend>Van and chimney assumptions</legend>
      <div class="layout-input-grid">
        <label>Finished floor to ceiling (mm)<input name="ceilingHeight" type="number" min="1200" max="2500" step="1" value="2000" required></label>
        <label>Twin-wall above outer roof (mm, cap excluded)<input name="projection" type="number" min="0" max="1200" step="1" value="300" required></label>
      </div>
      <details>
        <summary>Edit van dimensions and roof build-up</summary>
        <p class="layout-note">Editable, unmeasured finished-space assumptions.</p>
        <div class="layout-input-grid">
          <label>Load-bay length (mm)<input name="vanLength" type="number" min="1500" max="5000" step="1" value="3494" required></label>
          <label>Usable interior width (mm)<input name="vanWidth" type="number" min="1000" max="2200" step="1" value="1750" required></label>
          <label>Ceiling to outer roof (mm)<input name="roofBuildUp" type="number" min="0" max="250" step="1" value="80" required></label>
        </div>
      </details>
      <p class="layout-note">The ordered 1000 mm DW13080 contributes <strong>940 mm effective span</strong>. It is fixed in this model. Changing stove height does not move its top.</p>
    </fieldset>
    <button type="reset">Reset planning assumptions</button>
  </form>
  <p id="layout-input-error" class="layout-alert" role="alert" hidden></p>
  <div id="layout-results" hidden>
    <section class="layout-readout" aria-label="Derived dimensions">
      <h2>Height budget</h2>
      <dl id="layout-metrics"></dl>
      <p class="layout-note">The gap below the insulated section includes the connector; it is not a cut length for single-wall pipe. Terminal/cap height and joint allowances are excluded. Draft is not calculated.</p>
    </section>
    <div id="layout-conflicts" class="layout-alert" aria-live="polite"></div>
    <figure class="layout-live-figure">
      <svg id="layout-plan" role="img" aria-labelledby="layout-plan-title layout-plan-description"></svg>
      <figcaption>Plan view: front of load bay at left; rear doors at right. Driver/left wall at top, passenger/right wall at bottom. Heavy orange edge: door. Dashed outlet marker: assumed centred flue, not a measured outlet. Swipe drawings horizontally on narrow screens.</figcaption>
    </figure>
    <figure class="layout-live-figure">
      <svg id="layout-side" role="img" aria-labelledby="layout-side-title layout-side-description"></svg>
      <figcaption>Side elevation on the same front-to-rear axis. Orange: stove envelope. Teal: symbolic mounting platform. Blue: insulated section. Dashed grey: available single-wall/connector gap. Cap and supports are not drawn.</figcaption>
    </figure>
  </div>
</section>
```

## Where The Numbers Come From

- **Boutique placeholder: 445 W x 285 D x 323 H mm.** The published height is
  with legs collapsed, not a verified operating envelope. Edit the size after
  measuring deployed legs, projections and the actual outlet.
  https://boutiquecamping.com/en-eu/products/traditional-wood-burning-stove?view=v2
- **3494 mm load-bay length** is a published L3 reference, not a finished-van
  measurement. The default **1750 mm usable width, 2000 mm finished height,
  80 mm roof build-up and 300 mm projection are exploratory assumptions**,
  not manufacturer requirements.
  https://vanreviewer.co.uk/ford/transit/dimensions/1801/
- **940 mm effective insulated span** is the selected 1000 mm DW-FU element's
  installed length. Its bottom is derived from the fixed pipe-top position.
- Aisle-facing orientation puts body width along the van and depth across it.
  Cab/rear-facing orientations exchange those footprint axes.

The figures omit required hot clearances on purpose: no verified Boutique
values are available here. The selected wall offset is a geometric gap, not
a recommended clearance. See [technical holds](research.md#installation-holds)
and the [original figures](figures.md) before treating any arrangement as a
candidate for physical measurement.
