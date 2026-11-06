import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join, resolve } from "node:path";
import { defineConfig } from "vitepress";
import { graphApi } from "../../../scripts/blog_review_preview.mjs";

const blogRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = resolve(blogRoot, "../..");
const local = process.env.VAN_LOCAL_PREVIEW === "1";
const base = process.env.BLOG_BASE ?? (local ? "/" : "/Van/");
const port = Number(process.env.VAN_REVIEW_PORT ?? 8766);
// Published heading links use ASCII words and omit numeric section prefixes.
const headingId = title => title.normalize("NFKD").toLowerCase()
  .replace(/[\u0300-\u036f]/g, "")
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/^[^a-z]+/, "")
  .replace(/-+$/, "");
const plugins = [];
if (process.env.VAN_REVIEW_CONNECTION_FILE) {
  const { previewComments } = await import(pathToFileURL(join(process.env.VAN_REVIEW_PACKAGE, "scripts/preview_comments/vite-plugin.mjs")));
  plugins.push(previewComments({ connectionFile: process.env.VAN_REVIEW_CONNECTION_FILE }));
}
plugins.push({
  name: "van-local-shopping",
  configureServer(server) {
    server.middlewares.use((request, response, next) => {
      const url = new URL(request.url, `http://127.0.0.1:${port}`);
      if (url.pathname.endsWith(".html") &&
          !url.pathname.startsWith("/_static/") && !url.pathname.startsWith("/_downloads/")) {
        response.writeHead(302, { Location: url.pathname.slice(0, -5) + url.search + url.hash });
        return response.end();
      }
      next();
    });
    server.middlewares.use(graphApi({
      origin: `http://127.0.0.1:${port}`,
      jsonPath: join(blogRoot, "_static/shopping_graph.json"),
      dbPath: join(repoRoot, "docs/shopping_graph.sqlite"),
      buildDir: join(blogRoot, "_build/html"),
    }));
  },
});

export default defineConfig({
  title: "The Van Build",
  description: "Ford Transit L3H3 conversion: plans, parts and construction.",
  base,
  cleanUrls: true,
  markdown: { anchor: { slugify: headingId } },
  srcExclude: ["**/README.md", "_build/**", "node_modules/**", "public/**"],
  outDir: join(blogRoot, "_build/html"),
  cacheDir: join(blogRoot, "_build/vitepress-cache"),
  head: [
    ["link", { rel: "icon", href: "data:," }],
    ["link", { rel: "stylesheet", href: `${base}_static/stove.css` }],
    ["script", { src: `${base}_static/shopping-graph.js`, defer: "", "data-clean-urls": "true", "data-local-only": local ? "true" : "false" }],
  ],
  transformPageData(page) {
    if (readFileSync(join(blogRoot, page.relativePath), "utf8").includes("js-shopping-graph")) {
      page.frontmatter.aside = false;
    }
  },
  themeConfig: {
    nav: [
      { text: "Build", link: "/" },
      { text: "Work packages", link: "/work-packages" },
      { text: "Shopping", link: "/shopping-graph" },
      { text: "Useful places", link: "/useful-places" },
    ],
    sidebar: [
      { text: "Build overview", items: [
        { text: "Dashboard", link: "/" },
        { text: "Work packages", link: "/work-packages" },
        { text: "Shopping graph", link: "/shopping-graph" },
        { text: "Useful places", link: "/useful-places" },
      ] },
      { text: "Heater", items: [
        { text: "Removal record", link: "/heater_removal/" },
        { text: "Planar 44D relocation", link: "/diesel_heater/" },
      ] },
      { text: "Floor", items: [
        { text: "Overview", link: "/floor/" },
        { text: "Rivet-hole sealing", link: "/floor/rivet_holes" },
        { text: "Replacement air", link: "/floor/replacement_air" },
        { text: "Levelling and XPS", link: "/floor/levelling" },
      ] },
      { text: "Roof", items: [{ text: "MaxxFan installation", link: "/maxxfan/" }] },
      { text: "Wood stove", items: [
        { text: "Overview", link: "/wood_stove/" },
        { text: "Installation and status", link: "/wood_stove/installation-plan" },
        { text: "Shopping list", link: "/wood_stove/shopping_list_boutique" },
        { text: "Build story", link: "/wood_stove/story/" },
        { text: "1. What the stove is for", link: "/wood_stove/story/01-what-the-stove-is-for" },
        { text: "2. Choosing the stove", link: "/wood_stove/story/02-choosing-the-stove" },
        { text: "3. Sourcing the chimney", link: "/wood_stove/story/03-sourcing-the-chimney" },
        { text: "Chimney figure", link: "/wood_stove/figures" },
        { text: "Research", link: "/wood_stove/research" },
      ] },
      { text: "Later work", items: [
        { text: "Electronics diagnostics", link: "/electronics/clamp_meter" },
        { text: "Front seat swivels", link: "/seats/front_swivels" },
      ] },
    ],
    outline: [2, 3],
    search: { provider: "local" },
  },
  vite: {
    plugins,
    server: { host: "127.0.0.1", port, strictPort: true },
  },
});
