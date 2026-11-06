import { spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const blogRoot = join(repoRoot, "docs/blog");

export function saveShoppingGraph(graph, jsonPath, dbPath, buildDir) {
  const code = [
    "import json, sys",
    "from pathlib import Path",
    "from scripts.shopping_graph import save_graph",
    "saved = save_graph(json.load(sys.stdin), json_path=Path(sys.argv[1]), db_path=Path(sys.argv[2]), build_html_dir=Path(sys.argv[3]))",
    "print(json.dumps({'ok': True, 'graph': saved}))",
  ].join("\n");
  return new Promise((accept, reject) => {
    const child = spawn("python3", ["-B", "-c", code, jsonPath, dbPath, buildDir], { cwd: repoRoot });
    let output = "", error = "";
    child.stdout.on("data", chunk => { output += chunk; });
    child.stderr.on("data", chunk => { error += chunk; });
    child.on("error", reject);
    child.on("close", status => {
      if (status !== 0) reject(new Error(error || `Graph save exited with ${status}`));
      else {
        try { accept(JSON.parse(output)); } catch (failure) { reject(failure); }
      }
    });
    child.stdin.on("error", reject);
    child.stdin.end(JSON.stringify(graph));
  });
}

export function graphApi({ origin, jsonPath, dbPath, buildDir }) {
  return async (request, response, next) => {
    if (request.url?.split("?")[0] !== "/api/graph") return next();
    response.setHeader("Content-Type", "application/json");
    response.setHeader("Cache-Control", "no-store");
    try {
      if (request.headers.host !== new URL(origin).host ||
          (request.headers.origin && request.headers.origin !== origin)) {
        response.statusCode = 403;
        return response.end(JSON.stringify({ ok: false, error: "Local preview origin required" }));
      }
      if (request.method === "GET") return response.end(readFileSync(jsonPath, "utf8"));
      if (request.method !== "POST") {
        response.statusCode = 405;
        return response.end(JSON.stringify({ ok: false, error: "Use GET or POST" }));
      }
      if (!request.headers["content-type"]?.startsWith("application/json")) {
        response.statusCode = 415;
        return response.end(JSON.stringify({ ok: false, error: "JSON required" }));
      }
      let raw = "";
      for await (const chunk of request) {
        raw += chunk;
        if (Buffer.byteLength(raw) > 2 * 1024 * 1024) throw new Error("Graph exceeds 2 MiB");
      }
      const graph = JSON.parse(raw);
      if (!Array.isArray(graph?.nodes) || !Array.isArray(graph?.edges)) {
        throw new Error("Graph requires nodes and edges arrays");
      }
      response.end(JSON.stringify(await saveShoppingGraph(graph, jsonPath, dbPath, buildDir)));
    } catch (error) {
      console.error(`Shopping graph request failed: ${error.message}`);
      response.statusCode = 400;
      response.end(JSON.stringify({ ok: false, error: error.message }));
    }
  };
}

export async function startReview({ reviewPackage, connectionFile, port = 8766 }) {
  if (Boolean(reviewPackage) !== Boolean(connectionFile)) throw new Error("Comments require a package and connection file");
  if (connectionFile && !existsSync(connectionFile)) throw new Error("Comment connection file missing; load the session extension first");
  process.env.VAN_LOCAL_PREVIEW = "1";
  process.env.BLOG_BASE = "/";
  process.env.VAN_REVIEW_PORT = String(port);
  if (connectionFile) {
    process.env.VAN_REVIEW_PACKAGE = resolve(reviewPackage);
    process.env.VAN_REVIEW_CONNECTION_FILE = resolve(connectionFile);
  }
  const require = createRequire(join(blogRoot, "package.json"));
  const { createServer } = await import(pathToFileURL(require.resolve("vitepress")));
  const server = await createServer(blogRoot, { host: "127.0.0.1", port, strictPort: true });
  try {
    await server.listen();
    console.log(`Van Build: http://127.0.0.1:${port}/`);
    return { server, close: () => server.close() };
  } catch (error) {
    await server.close();
    throw error;
  }
}
