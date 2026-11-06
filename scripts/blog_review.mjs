#!/usr/bin/env node
import { parseArgs } from "node:util";
import { startReview } from "./blog_review_preview.mjs";

const { values } = parseArgs({ options: {
  "review-package": { type: "string" },
  "connection-file": { type: "string" },
  port: { type: "string", default: "8766" },
} });
if (Boolean(values["review-package"]) !== Boolean(values["connection-file"])) {
  throw new Error("Comments require both --review-package and --connection-file");
}
const port = Number(values.port);
if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error("Invalid port");
const preview = await startReview({ reviewPackage: values["review-package"], connectionFile: values["connection-file"], port });
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.once(signal, async () => { await preview.close(); process.exit(0); });
}
