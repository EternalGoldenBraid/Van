import assert from "node:assert/strict";
import test from "node:test";
import { calculateLayout } from "../_static/layout-explorer.mjs";

const baseline = {
    stoveWidth: 445, stoveDepth: 285, stoveHeight: 323,
    side: "driver", orientation: "aisle",
    mountHeight: 0, position: 750, wallGap: 150,
    vanLength: 3494, vanWidth: 1750,
    ceilingHeight: 2000, roofBuildUp: 80, projection: 300,
};

test("fixed exterior height: raising the stove reduces the connector gap and rise equally", () => {
    const floor = calculateLayout(baseline);
    assert.equal(floor.gap, 1117);
    assert.equal(floor.indoorTwin, 560);
    assert.equal(floor.rise, 2057);
    assert.deepEqual(floor.warnings, []);
    for (const height of [300, 500]) {
        const raised = calculateLayout({ ...baseline, mountHeight: height });
        assert.equal(raised.pipeTop, floor.pipeTop);
        assert.equal(raised.pipeBottom, floor.pipeBottom);
        assert.equal(raised.indoorTwin, floor.indoorTwin);
        assert.equal(raised.gap, floor.gap - height);
        assert.equal(raised.rise, floor.rise - height);
    }
});

test("changing wall and orientation mirrors placement and exchanges footprint axes", () => {
    const driver = calculateLayout(baseline);
    const passenger = calculateLayout({ ...baseline, side: "passenger" });
    assert.equal(driver.top + passenger.top + driver.across, baseline.vanWidth);
    for (const orientation of ["rear", "cab"]) {
        const turned = calculateLayout({ ...baseline, orientation });
        assert.equal(turned.along, baseline.stoveDepth);
        assert.equal(turned.across, baseline.stoveWidth);
        assert.equal(turned.left + turned.along / 2, baseline.position);
        assert.equal(turned.rise, driver.rise);
    }
});

test("roof changes move the insulation split while extra projection reduces indoor insulation", () => {
    const original = calculateLayout(baseline);
    const higherRoof = calculateLayout({ ...baseline, ceilingHeight: 2100 });
    assert.equal(higherRoof.pipeTop, original.pipeTop + 100);
    assert.equal(higherRoof.gap, original.gap + 100);
    assert.equal(higherRoof.indoorTwin, original.indoorTwin);
    const higherPipe = calculateLayout({ ...baseline, projection: 450 });
    assert.equal(higherPipe.indoorTwin, original.indoorTwin - 150);
    assert.equal(higherPipe.gap, original.gap + 150);
});

test("incompatible boxes and pipe spans remain explicit, including negative gaps", () => {
    const invalid = calculateLayout({
        ...baseline, mountHeight: 1000, stoveHeight: 1500,
        position: 0, wallGap: 1500,
    });
    assert.equal(invalid.gap, -1060);
    assert.equal(invalid.warnings.length, 3);
    assert.ok(invalid.warnings.some(message => message.includes("load bay")));
    assert.ok(invalid.warnings.some(message => message.includes("ceiling")));
    assert.ok(invalid.warnings.some(message => message.includes("no positive gap")));
    const noIndoorSpan = calculateLayout({ ...baseline, projection: 1200 });
    assert.ok(noIndoorSpan.indoorTwin < 0);
    assert.ok(noIndoorSpan.warnings.some(message => message.includes("no span below")));
    const noProjection = calculateLayout({ ...baseline, projection: 0 });
    assert.ok(noProjection.warnings.some(message => message.includes("No twin-wall projection")));
});
