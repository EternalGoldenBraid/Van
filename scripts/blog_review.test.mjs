import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { graphApi } from "./blog_review_preview.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
test("publishes every blog page at its existing HTML path under the Pages base", () => {
  const blog = join(root, "docs/blog");
  let count = 0;
  function visit(directory) {
    for (const entry of readdirSync(join(blog, directory), { withFileTypes: true })) {
      if (entry.name.startsWith(".") || ["node_modules", "_build", "public"].includes(entry.name)) continue;
      const path = join(directory, entry.name);
      if (entry.isDirectory()) visit(path);
      else if (entry.name.endsWith(".md") && entry.name !== "README.md") {
        const html = readFileSync(join(blog, "_build/html", path.replace(/\.md$/, ".html")), "utf8");
        assert.match(html, /\/Van\/assets\//, path);
        assert.match(html, /<h1\b/, path);
        assert.doesNotMatch(html, /```\{(?:figure|raw|include|toctree)\}/, path);
        count++;
      }
    }
  }
  visit("");
  assert.equal(count, 24);
  for (const asset of [
    "_static/shopping_graph.json", "_static/figures/chimney-drawio.png",
    "diesel_heater/images/installation_02.jpg", "heater_removal/images/302.jpg",
    "downloads/window_plan.md", "downloads/floor_plan.md", "downloads/floor_sealing_logbook.md",
    "downloads/roof_layout_plan.md", "downloads/boutique-chimney-plan.drawio",
    "_downloads/b6c291e50525f334288fe48696c7eeeb/boutique-chimney-plan.drawio",
  ]) assert.ok(existsSync(join(blog, "_build/html", asset)), asset);
});

test("stove checkout records include delivery and fees without inventing paid expenditure", () => {
  const graph = JSON.parse(readFileSync(join(root, "docs/blog/_static/shopping_graph.json"), "utf8"));
  const ids = [
    "item:jeremias_dw37f080", "item:jeremias_dw13080", "item:jeremias_dw1076080",
    "item:master_flash_sq402ra", "item:stove_feuerdepot_delivery",
    "item:stove_hobby_hall_delivery", "item:stove_hobby_hall_fee",
  ];
  const items = ids.map(id => {
    const node = graph.nodes.find(node => node.id === id);
    assert.ok(node, id);
    assert.ok(graph.edges.some(edge => edge.shopping_item_id === id && edge.work_package_id === "wp:wood_stove"), id);
    assert.equal(node.actual_spend_eur ?? null, null);
    return node;
  });
  assert.equal(Math.round(items.reduce((sum, node) => sum + node.price_eur, 0) * 100), 39416);
  assert.equal(items[0].baseline_estimate_eur, 45);
  assert.equal(items[1].baseline_estimate_eur, 190);
  assert.equal(items[2].baseline_estimate_eur, 95);
  assert.equal(items[3].baseline_estimate_eur, 60);
  const source = readFileSync(join(root, "docs/blog/wood_stove/shopping_list_boutique.md"), "utf8");
  assert.doesNotMatch(source, /Recorded Order Costs|Included Parts And Installation Checks/);
});

test("shopping API reads without rewriting and saves through the existing graph synchronizer", async () => {
  const directory = mkdtempSync(join(tmpdir(), "van-graph-test-"));
  const jsonPath = join(directory, "graph.json");
  const dbPath = join(directory, "graph.sqlite");
  const original = readFileSync(join(root, "docs/blog/_static/shopping_graph.json"), "utf8");
  writeFileSync(jsonPath, original);
  let origin;
  const server = createServer((request, response) => graphApi({
    origin, jsonPath, dbPath, buildDir: join(directory, "build"),
  })(request, response, () => { response.statusCode = 404; response.end(); }));
  try {
    await new Promise(accept => server.listen(0, "127.0.0.1", accept));
    origin = `http://127.0.0.1:${server.address().port}`;
    const response = await fetch(`${origin}/api/graph`);
    const graph = await response.json();
    assert.equal(readFileSync(jsonPath, "utf8"), original);
    const stove = graph.nodes.find(node => node.id === "wp:wood_stove");
    stove.name = "Fixture stove name";
    const forbidden = await fetch(`${origin}/api/graph`, {
      method: "POST", headers: { Origin: "https://example.com", "Content-Type": "application/json" },
      body: JSON.stringify(graph),
    });
    assert.equal(forbidden.status, 403);
    assert.equal(readFileSync(jsonPath, "utf8"), original);
    const saved = await fetch(`${origin}/api/graph`, {
      method: "POST", headers: { Origin: origin, "Content-Type": "application/json" },
      body: JSON.stringify(graph),
    });
    const result = await saved.json();
    assert.equal(result.ok, true, JSON.stringify(result));
    assert.equal(JSON.parse(readFileSync(jsonPath, "utf8")).nodes.find(node => node.id === stove.id).name, stove.name);
    assert.ok(readFileSync(dbPath).length > 0);
    const invalid = await fetch(`${origin}/api/graph`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: "{}",
    });
    assert.equal(invalid.status, 400);
    assert.match((await invalid.json()).error, /nodes and edges/);
  } finally {
    await new Promise(accept => server.close(accept));
    rmSync(directory, { recursive: true, force: true });
  }
});

test("the existing Python server serves VitePress clean URLs and the Pages asset prefix", async () => {
  const directory = mkdtempSync(join(tmpdir(), "van-static-test-"));
  const child = spawn("python3", ["-B", "-u", "-c",
    "from pathlib import Path; import sys; from scripts.shopping_graph import run_server; run_server(0, '127.0.0.1', Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))",
    join(directory, "graph.json"), join(directory, "graph.sqlite"), join(root, "docs/blog/_build/html")],
  { cwd: root });
  let diagnostics = "";
  child.stderr.on("data", chunk => { diagnostics += chunk; });
  try {
    const origin = await new Promise((accept, reject) => {
      child.once("error", reject);
      child.once("exit", code => reject(new Error(`Static server exited ${code}: ${diagnostics}`)));
      child.stdout.on("data", chunk => {
        const match = /http:\/\/127\.0\.0\.1:\d+/.exec(String(chunk));
        if (match) accept(match[0]);
      });
    });
    for (const path of [
      "/Van/floor/rivet_holes", "/Van/floor/rivet_holes.html",
      "/Van/_static/shopping-graph.js",
      "/Van/_downloads/8ad89b826aad1bf0267c92bb456c0f19/window_plan.md",
    ]) assert.equal((await fetch(origin + path)).status, 200, path);
  } finally {
    if (child.pid && child.exitCode === null && child.signalCode === null) {
      const exited = new Promise(accept => child.once("exit", accept));
      child.kill("SIGTERM");
      await exited;
    }
    rmSync(directory, { recursive: true, force: true });
  }
});
