const INSULATED_SPAN = 940;
const BOUTIQUE = { stoveWidth: 445, stoveDepth: 285, stoveHeight: 323 };

// Inputs are constrained by the form before entering the geometric model.
export function calculateLayout(state) {
    const along = state.orientation === "aisle" ? state.stoveWidth : state.stoveDepth;
    const across = state.orientation === "aisle" ? state.stoveDepth : state.stoveWidth;
    const left = state.position - along / 2;
    const top = state.side === "driver"
        ? state.wallGap
        : state.vanWidth - state.wallGap - across;
    const stoveTop = state.mountHeight + state.stoveHeight;
    const roof = state.ceilingHeight + state.roofBuildUp;
    const pipeTop = roof + state.projection;
    const pipeBottom = pipeTop - INSULATED_SPAN;
    const warnings = [];

    if (left < 0 || left + along > state.vanLength || top < 0 || top + across > state.vanWidth) {
        warnings.push("The stove body extends beyond the modelled load bay.");
    }
    if (stoveTop >= state.ceilingHeight) {
        warnings.push("The stove envelope reaches or crosses the finished ceiling.");
    }
    if (pipeBottom >= state.ceilingHeight) {
        warnings.push("The insulated section has no span below the finished ceiling.");
    }
    if (pipeBottom <= stoveTop) {
        warnings.push("There is no positive gap for single-wall pipe and the connector below the insulated section.");
    }
    if (state.projection === 0) {
        warnings.push("No twin-wall projection above the outer roof is modelled.");
    }
    return {
        along, across, left, top, stoveTop, roof, pipeTop, pipeBottom,
        gap: pipeBottom - stoveTop,
        indoorTwin: state.ceilingHeight - pipeBottom,
        rise: pipeTop - stoveTop,
        warnings,
    };
}

function svgNode(tag, attributes, text) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [key, value] of Object.entries(attributes)) {
        node.setAttribute(key, value);
    }
    if (text !== undefined) node.textContent = text;
    return node;
}

function beginDrawing(svg, title, description, height) {
    svg.setAttribute("viewBox", `0 0 1000 ${height}`);
    svg.replaceChildren(
        svgNode("title", { id: `${svg.id}-title` }, title),
        svgNode("desc", { id: `${svg.id}-description` }, description),
    );
    return {
        rect: (x, y, width, boxHeight, className) =>
            svg.append(svgNode("rect", { x, y, width, height: boxHeight, class: className })),
        line: (x1, y1, x2, y2, className) =>
            svg.append(svgNode("line", { x1, y1, x2, y2, class: className })),
        text: (x, y, text, anchor = "start") =>
            svg.append(svgNode("text", { x, y, "text-anchor": anchor }, text)),
    };
}

function drawLayout(state, model) {
    const minX = Math.min(0, model.left);
    const maxX = Math.max(state.vanLength, model.left + model.along);
    const scale = 800 / (maxX - minX);
    const x = value => 100 + (value - minX) * scale;
    const minY = Math.min(0, model.top);
    const maxY = Math.max(state.vanWidth, model.top + model.across);
    const y = value => 90 + (value - minY) * scale;
    const planHeight = (maxY - minY) * scale + 180;
    const plan = document.querySelector("#layout-plan");
    const p = beginDrawing(plan, "Stove plan view",
        `${state.side} side, door facing ${state.orientation}. Body footprint ${model.along} mm along the van by ${model.across} mm across it.`,
        planHeight);
    p.text(30, 30, "PLAN VIEW");
    p.rect(x(0), y(0), state.vanLength * scale, state.vanWidth * scale, "layout-van");
    p.text(x(0), y(0) - 20, "Driver / left");
    p.text(x(0), y(state.vanWidth) + 35, "Passenger / right");
    p.text(x(0), planHeight - 15, "Front / cab");
    p.text(x(state.vanLength), planHeight - 15, "Rear doors", "end");
    const sx = x(model.left), sy = y(model.top);
    const sw = model.along * scale, sd = model.across * scale;
    p.rect(sx, sy, sw, sd, "layout-stove");
    if (state.orientation === "rear") {
        p.line(sx + sw, sy, sx + sw, sy + sd, "layout-door");
    } else if (state.orientation === "cab") {
        p.line(sx, sy, sx, sy + sd, "layout-door");
    } else {
        const doorY = state.side === "driver" ? sy + sd : sy;
        p.line(sx, doorY, sx + sw, doorY, "layout-door");
    }
    plan.append(svgNode("circle", {
        cx: x(state.position), cy: sy + sd / 2, r: 40 * scale, class: "layout-outlet",
    }));

    const minZ = Math.min(0, model.pipeBottom);
    const maxZ = Math.max(model.pipeTop, model.stoveTop);
    const sideHeight = (maxZ - minZ) * scale + 180;
    const z = value => 90 + (maxZ - value) * scale;
    const side = document.querySelector("#layout-side");
    const e = beginDrawing(side, "Stove side elevation",
        `Mounting elevation ${state.mountHeight} mm. Insulated pipe start ${model.pipeBottom} mm and top ${model.pipeTop} mm above the finished floor. Available connector and single-wall gap ${model.gap} mm.`,
        sideHeight);
    e.text(30, 30, "SIDE ELEVATION");
    e.rect(x(0), z(state.ceilingHeight), state.vanLength * scale,
        state.ceilingHeight * scale, "layout-van");
    e.rect(x(0), z(model.roof), state.vanLength * scale,
        state.roofBuildUp * scale, "layout-roof");
    e.line(x(0), z(state.ceilingHeight), x(state.vanLength), z(state.ceilingHeight), "layout-ceiling");
    const labelAtRear = state.position < state.vanLength / 2;
    const roofLabelX = labelAtRear ? x(state.vanLength) : x(0);
    const roofAnchor = labelAtRear ? "end" : "start";
    e.text(roofLabelX, z(model.roof) - 15, "Outer roof", roofAnchor);
    e.text(roofLabelX + (labelAtRear ? -10 : 10),
        z(state.ceilingHeight) + 30, "Ceiling", roofAnchor);
    e.line(x(0), z(0), x(state.vanLength), z(0), "layout-floor");
    e.text(x(0), z(0) + 35, "Finished floor");
    if (state.mountHeight > 0) {
        e.rect(sx, z(state.mountHeight), sw, state.mountHeight * scale, "layout-mount");
    } else {
        e.line(sx, z(0), sx + sw, z(0), "layout-mount");
    }
    e.rect(sx, z(model.stoveTop), sw, state.stoveHeight * scale, "layout-stove");
    const pipeX = x(state.position);
    e.line(pipeX, z(model.stoveTop), pipeX, z(model.pipeBottom), "layout-single");
    e.rect(pipeX - 72.5 * scale, z(model.pipeTop), 145 * scale,
        INSULATED_SPAN * scale, "layout-twin");
    const labelRight = pipeX < 650;
    e.text(pipeX + (labelRight ? 25 : -25), z(model.pipeTop) - 15,
        "Pipe top (no cap)", labelRight ? "start" : "end");
}

function updateReadout(state, model) {
    const rows = [
        ["Stove top above floor", model.stoveTop],
        ["Insulated pipe top above floor", model.pipeTop],
        ["Insulated start above floor", model.pipeBottom],
        ["Insulated span below ceiling", model.indoorTwin],
        ["Single-wall + connector gap", model.gap],
        ["Stove-top to pipe-top rise", model.rise],
    ];
    const metrics = document.querySelector("#layout-metrics");
    metrics.replaceChildren();
    for (const [label, value] of rows) {
        const term = document.createElement("dt");
        term.textContent = label;
        const detail = document.createElement("dd");
        detail.textContent = `${value} mm`;
        metrics.append(term, detail);
    }
    const conflicts = document.querySelector("#layout-conflicts");
    conflicts.replaceChildren();
    conflicts.classList.toggle("has-conflicts", model.warnings.length > 0);
    if (model.warnings.length) {
        const heading = document.createElement("strong");
        heading.textContent = "Geometric conflicts in this model:";
        const list = document.createElement("ul");
        for (const warning of model.warnings) {
            const item = document.createElement("li");
            item.textContent = warning;
            list.append(item);
        }
        conflicts.append(heading, list);
    } else {
        conflicts.textContent = "Only body bounds and vertical intersections are checked. Required hot clearances remain unknown; these gaps are not approval.";
    }
    document.querySelector("#stove-dimension-note").textContent = state.preset === "boutique"
        ? "Published 445 x 285 x 323 mm placeholder; height is with legs collapsed. Measure deployed legs, projections and outlet. Editing a dimension selects Custom."
        : "Custom envelope: enter measured or explicitly assumed dimensions. No manufacturer clearances or operating limits are inferred.";
}

function initialiseLayout() {
    const form = document.querySelector("#stove-layout-form");
    if (!form) return;
    const results = document.querySelector("#layout-results");
    const error = document.querySelector("#layout-input-error");
    const update = () => {
        const invalid = [...form.elements].find(element => element.validity && !element.validity.valid);
        error.hidden = !invalid;
        results.hidden = Boolean(invalid);
        if (invalid) {
            error.textContent = `Preview paused: ${invalid.closest("label").firstChild.textContent.trim()}. ${invalid.validationMessage}`;
            return;
        }
        const state = Object.fromEntries(new FormData(form));
        for (const field of form.querySelectorAll('input[type="number"]')) {
            state[field.name] = field.valueAsNumber;
        }
        const model = calculateLayout(state);
        updateReadout(state, model);
        drawLayout(state, model);
    };
    form.addEventListener("input", event => {
        if (Object.hasOwn(BOUTIQUE, event.target.name)) form.elements.preset.value = "custom";
        if (event.target.name === "preset" && event.target.value === "boutique") {
            for (const [name, value] of Object.entries(BOUTIQUE)) form.elements[name].value = value;
        }
        if (event.target.name === "preset" && event.target.value === "custom") {
            form.querySelector("#stove-size-details").open = true;
        }
        update();
    });
    form.addEventListener("submit", event => event.preventDefault());
    form.addEventListener("reset", () => requestAnimationFrame(update));
    update();
}

function initialiseFigures() {
    const images = document.querySelectorAll('figure[id^="fig-chimney-"] img');
    if (!images.length) return;
    const dialog = document.createElement("dialog");
    dialog.className = "figure-lightbox is-fitted";
    dialog.setAttribute("aria-label", "Expanded diagram");
    const toolbar = document.createElement("div");
    toolbar.className = "figure-lightbox-toolbar";
    const zoom = document.createElement("button");
    zoom.type = "button";
    zoom.textContent = "Actual size";
    const close = document.createElement("button");
    close.type = "button";
    close.textContent = "Close figure";
    const image = document.createElement("img");
    zoom.addEventListener("click", () => {
        const fitted = dialog.classList.toggle("is-fitted");
        zoom.textContent = fitted ? "Actual size" : "Fit to window";
    });
    close.addEventListener("click", () => dialog.close());
    toolbar.append(zoom, close);
    dialog.append(toolbar, image);
    document.body.append(dialog);
    for (const original of images) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "figure-expand";
        button.textContent = "Expand figure";
        button.setAttribute("aria-haspopup", "dialog");
        button.addEventListener("click", () => {
            image.src = original.currentSrc;
            image.alt = original.alt;
            dialog.classList.add("is-fitted");
            zoom.textContent = "Actual size";
            dialog.showModal();
        });
        original.after(button);
    }
}

if (typeof document !== "undefined") {
    initialiseLayout();
    initialiseFigures();
}
