#!/usr/bin/env python3
"""Bipartite graph database & local server for Van Build work packages and shopping items.

Source of truth:
- `docs/blog/_static/shopping_graph.json` (versioned in Git, loaded by GitHub Pages,
  and editable via the browser UI or this CLI)
- `docs/shopping_graph.sqlite` (SQLite mirror automatically kept in sync for SQL queries)

CLI usage:
  python3 scripts/shopping_graph.py summary
  python3 scripts/shopping_graph.py package floor_rivet_holes
  python3 scripts/shopping_graph.py shared
  python3 scripts/shopping_graph.py pending
  python3 scripts/shopping_graph.py set-status 10129724 ordered --date 2026-10-26
  python3 scripts/shopping_graph.py add --name "Sikaflex-221" --status planned --packages maxxfan,floor_replacement_air
  python3 scripts/shopping_graph.py remove item:sikaflex_221
  python3 scripts/shopping_graph.py serve --port 8000
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = REPO_ROOT / "docs" / "shopping_graph.sqlite"
DEFAULT_STATIC_JSON = REPO_ROOT / "docs" / "blog" / "_static" / "shopping_graph.json"
DEFAULT_BUILD_HTML = REPO_ROOT / "docs" / "blog" / "_build" / "html"

NODE_TYPES = ("work_package", "shopping_item")
VALID_ITEM_STATUSES = ("owned", "bought", "ordered", "planned", "candidate", "tbd")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL CHECK (node_type IN ('work_package', 'shopping_item')),
    name TEXT NOT NULL,
    status TEXT,
    sku TEXT,
    supplier TEXT,
    qty TEXT,
    url TEXT,
    ordered_date TEXT,
    doc_path TEXT,
    notes TEXT,
    price_eur REAL,
    price_basis TEXT
);

CREATE TABLE IF NOT EXISTS edges (
    work_package_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    shopping_item_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'required',
    notes TEXT,
    PRIMARY KEY (work_package_id, shopping_item_id)
);

CREATE VIEW IF NOT EXISTS v_bipartite_shopping AS
SELECT
    wp.id AS work_package_id,
    wp.name AS work_package,
    si.id AS item_id,
    si.name AS item_name,
    si.status AS status,
    si.qty AS qty,
    si.supplier AS supplier,
    si.sku AS sku,
    si.ordered_date AS ordered_date,
    si.price_eur AS price_eur,
    e.role AS role,
    COALESCE(e.notes, si.notes, '') AS notes
FROM edges e
JOIN nodes wp ON wp.id = e.work_package_id AND wp.node_type = 'work_package'
JOIN nodes si ON si.id = e.shopping_item_id AND si.node_type = 'shopping_item';
"""


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:48] or "item"


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def load_graph_from_sqlite(conn: sqlite3.Connection) -> dict[str, Any]:
    nodes = [dict(r) for r in conn.execute("SELECT * FROM nodes ORDER BY node_type, id")]
    edges = [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM edges ORDER BY work_package_id, shopping_item_id"
        )
    ]
    return {"node_types": list(NODE_TYPES), "nodes": nodes, "edges": edges}


def save_graph(
    graph: dict[str, Any],
    json_path: Path = DEFAULT_STATIC_JSON,
    db_path: Path = DEFAULT_DB_PATH,
    build_html_dir: Path = DEFAULT_BUILD_HTML,
) -> dict[str, Any]:
    """Validate and persist bipartite graph to JSON, SQLite, and built HTML _static."""
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL.replace("CREATE VIEW IF NOT EXISTS v_bipartite_shopping AS", "CREATE VIEW IF NOT EXISTS v_bipartite_shopping AS"))
        existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(nodes)")}
        if "price_eur" not in existing_cols:
            conn.execute("ALTER TABLE nodes ADD COLUMN price_eur REAL")
        if "price_basis" not in existing_cols:
            conn.execute("ALTER TABLE nodes ADD COLUMN price_basis TEXT")
        conn.execute("DROP VIEW IF EXISTS v_bipartite_shopping")
        conn.executescript(SCHEMA_SQL[SCHEMA_SQL.index("CREATE VIEW IF NOT EXISTS v_bipartite_shopping AS"):])
        conn.execute("DELETE FROM edges;")
        conn.execute("DELETE FROM nodes;")

        for n in nodes:
            conn.execute(
                """
                INSERT INTO nodes (
                    id, node_type, name, status, sku, supplier, qty, url, ordered_date, doc_path, notes, price_eur, price_basis
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    n["id"],
                    n["node_type"],
                    n["name"],
                    n.get("status"),
                    n.get("sku"),
                    n.get("supplier"),
                    n.get("qty"),
                    n.get("url"),
                    n.get("ordered_date"),
                    n.get("doc_path"),
                    n.get("notes"),
                    n.get("price_eur"),
                    n.get("price_basis"),
                ),
            )

        node_ids = {n["id"] for n in nodes}
        for e in edges:
            wp_id = e["work_package_id"]
            si_id = e["shopping_item_id"]
            if wp_id in node_ids and si_id in node_ids:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO edges (work_package_id, shopping_item_id, role, notes)
                    VALUES (?, ?, ?, ?)
                    """,
                    (wp_id, si_id, e.get("role") or "required", e.get("notes")),
                )

        canonical = load_graph_from_sqlite(conn)

    payload = json.dumps(canonical, indent=2, ensure_ascii=False) + "\n"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(payload, encoding="utf-8")

    built_json = build_html_dir / "_static" / "shopping_graph.json"
    if built_json.parent.exists():
        built_json.write_text(payload, encoding="utf-8")

    return canonical


def ensure_synced(
    json_path: Path = DEFAULT_STATIC_JSON, db_path: Path = DEFAULT_DB_PATH
) -> sqlite3.Connection:
    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
        save_graph(data, json_path=json_path, db_path=db_path)
    return connect(db_path)


def normalize_wp_id(wp: str) -> str:
    wp = wp.strip()
    return wp if wp.startswith("wp:") else f"wp:{wp}"


def cmd_summary(conn: sqlite3.Connection) -> None:
    print("=== Bipartite Graph Summary (node_types = [work_package, shopping_item]) ===")
    counts = conn.execute(
        "SELECT node_type, COUNT(*) AS n FROM nodes GROUP BY node_type ORDER BY node_type"
    ).fetchall()
    edge_count = conn.execute("SELECT COUNT(*) AS n FROM edges").fetchone()["n"]
    print(
        ", ".join(f"{r['node_type']}: {r['n']}" for r in counts)
        + f", edges: {edge_count}\n"
    )

    rows = conn.execute(
        """
        SELECT
            wp.id,
            wp.name,
            wp.status AS wp_status,
            SUM(CASE WHEN si.status IN ('owned', 'bought') THEN 1 ELSE 0 END) AS owned,
            SUM(CASE WHEN si.status = 'ordered' THEN 1 ELSE 0 END) AS ordered,
            SUM(CASE WHEN si.status IN ('planned', 'candidate', 'tbd') THEN 1 ELSE 0 END) AS todo
        FROM nodes wp
        LEFT JOIN edges e ON e.work_package_id = wp.id
        LEFT JOIN nodes si ON si.id = e.shopping_item_id
        WHERE wp.node_type = 'work_package'
        GROUP BY wp.id, wp.name, wp.status
        ORDER BY wp.id
        """
    ).fetchall()
    print(f"{'Work Package ID':<26} {'Status':<10} {'Owned':>5} {'Ordered':>7} {'To Buy':>6}  Name")
    print("-" * 92)
    for r in rows:
        print(
            f"{r['id']:<26} {r['wp_status']:<10} {r['owned']:>5} {r['ordered']:>7} {r['todo']:>6}  {r['name']}"
        )


def cmd_package(conn: sqlite3.Connection, wp_query: str) -> None:
    wp_id = normalize_wp_id(wp_query)
    wp = conn.execute(
        "SELECT * FROM nodes WHERE id = ? AND node_type = 'work_package'", (wp_id,)
    ).fetchone()
    if not wp:
        raise SystemExit(f"Unknown work_package: {wp_query}")

    print(f"=== {wp['name']} ({wp['id']}) [{wp['status']}] ===")
    print(f"Doc: {wp['doc_path']}\n")
    rows = conn.execute(
        """
        SELECT item_id, item_name, status, qty, supplier, sku, ordered_date, role, notes
        FROM v_bipartite_shopping
        WHERE work_package_id = ?
        ORDER BY
            CASE status
                WHEN 'owned' THEN 1
                WHEN 'ordered' THEN 2
                WHEN 'planned' THEN 3
                WHEN 'candidate' THEN 4
                ELSE 5
            END,
            item_id
        """,
        (wp_id,),
    ).fetchall()
    for r in rows:
        sku_str = f" [{r['sku']}]" if r["sku"] else ""
        date_str = f" ({r['ordered_date']})" if r["ordered_date"] else ""
        print(
            f"- [{r['status'].upper()}{date_str}] {r['item_name']}{sku_str} "
            f"({r['qty']}, {r['supplier']}; {r['price_eur'] if r['price_eur'] is not None else 'price TBD'} €) — {r['notes']}"
        )


def cmd_shared(conn: sqlite3.Connection) -> None:
    print("=== Shared Shopping Items (degree >= 2 work packages) ===")
    rows = conn.execute(
        """
        SELECT
            si.id,
            si.name,
            si.status,
            si.sku,
            si.supplier,
            COUNT(e.work_package_id) AS deg,
            GROUP_CONCAT(REPLACE(e.work_package_id, 'wp:', ''), ', ') AS packages
        FROM nodes si
        JOIN edges e ON e.shopping_item_id = si.id
        WHERE si.node_type = 'shopping_item'
        GROUP BY si.id
        HAVING COUNT(e.work_package_id) >= 2
        ORDER BY deg DESC, si.id
        """
    ).fetchall()
    for r in rows:
        sku = f" ({r['sku']})" if r["sku"] else ""
        print(f"- [{r['status'].upper()}] {r['name']}{sku} -> {r['deg']} packages: {r['packages']}")


def cmd_pending(conn: sqlite3.Connection) -> None:
    print("=== Remaining Shopping Items To Buy (planned / candidate / tbd) ===")
    rows = conn.execute(
        """
        SELECT
            si.id,
            si.name,
            si.status,
            si.qty,
            si.supplier,
            si.sku,
            GROUP_CONCAT(REPLACE(e.work_package_id, 'wp:', ''), ', ') AS packages
        FROM nodes si
        JOIN edges e ON e.shopping_item_id = si.id
        WHERE si.node_type = 'shopping_item'
          AND si.status IN ('planned', 'candidate', 'tbd')
        GROUP BY si.id
        ORDER BY si.status, si.supplier, si.id
        """
    ).fetchall()
    for r in rows:
        sku = f" [{r['sku']}]" if r["sku"] else ""
        print(
            f"- [{r['status'].upper()}] {r['name']}{sku} ({r['qty']}, {r['supplier']}) "
            f"-> {r['packages']}"
        )


def cmd_set_status(
    conn: sqlite3.Connection, keys: list[str], status: str, date: str | None
) -> None:
    with conn:
        for key in keys:
            cur = conn.execute(
                """
                UPDATE nodes
                SET status = ?, ordered_date = COALESCE(?, ordered_date)
                WHERE node_type = 'shopping_item' AND (id = ? OR sku = ?)
                """,
                (status, date if status == "ordered" else None, key, key),
            )
            if cur.rowcount == 0:
                print(f"Warning: no shopping_item matched '{key}'")
            else:
                print(f"Updated '{key}' -> status={status}")


def cmd_add_item(
    conn: sqlite3.Connection,
    name: str,
    packages: list[str],
    item_id: str | None,
    status: str,
    qty: str | None,
    supplier: str | None,
    sku: str | None,
    url: str | None,
    ordered_date: str | None,
    notes: str | None,
    price_eur: float | None,
) -> None:
    new_id = item_id or f"item:{slugify(name)}"
    if not new_id.startswith("item:"):
        new_id = f"item:{new_id}"
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO nodes (
                id, node_type, name, status, sku, supplier, qty, url, ordered_date, notes, price_eur, price_basis
            )
            VALUES (?, 'shopping_item', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (new_id, name, status, sku, supplier, qty, url, ordered_date, notes, price_eur, "listed" if price_eur is not None else None),
        )
        conn.execute("DELETE FROM edges WHERE shopping_item_id = ?", (new_id,))
        for wp in packages:
            wp_id = normalize_wp_id(wp)
            conn.execute(
                """
                INSERT OR IGNORE INTO edges (work_package_id, shopping_item_id, role, notes)
                VALUES (?, ?, 'required', ?)
                """,
                (wp_id, new_id, notes),
            )
    print(f"Added/updated {new_id} ({name}) linked to {[normalize_wp_id(p) for p in packages]}")


def cmd_remove_item(conn: sqlite3.Connection, key: str) -> None:
    with conn:
        row = conn.execute(
            "SELECT id, name FROM nodes WHERE node_type = 'shopping_item' AND (id = ? OR sku = ?)",
            (key, key),
        ).fetchone()
        if not row:
            print(f"Warning: no shopping_item matched '{key}'")
            return
        conn.execute("DELETE FROM edges WHERE shopping_item_id = ?", (row["id"],))
        conn.execute("DELETE FROM nodes WHERE id = ?", (row["id"],))
        print(f"Removed {row['id']} ({row['name']})")


def run_server(
    port: int,
    bind: str,
    json_path: Path,
    db_path: Path,
    build_html_dir: Path,
) -> None:
    class GraphHTTPRequestHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(build_html_dir), **kwargs)

        def do_GET(self) -> None:
            if self.path.split("?")[0] == "/api/graph":
                with ensure_synced(json_path, db_path) as conn:
                    data = load_graph_from_sqlite(conn)
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            super().do_GET()

        def do_POST(self) -> None:
            if self.path.split("?")[0] == "/api/graph":
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                try:
                    incoming = json.loads(raw.decode("utf-8"))
                    saved = save_graph(
                        incoming,
                        json_path=json_path,
                        db_path=db_path,
                        build_html_dir=build_html_dir,
                    )
                except Exception as exc:  # noqa: BLE001
                    err = json.dumps({"ok": False, "error": str(exc)}).encode("utf-8")
                    self.send_response(HTTPStatus.BAD_REQUEST)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(err)))
                    self.end_headers()
                    self.wfile.write(err)
                    return

                resp = json.dumps({"ok": True, "graph": saved}, ensure_ascii=False).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
                return

            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    server = ThreadingHTTPServer((bind, port), GraphHTTPRequestHandler)
    print(f"Serving blog & /api/graph on http://{bind}:{port}/")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Path to SQLite database")
    parser.add_argument("--json", type=Path, default=DEFAULT_STATIC_JSON, help="Path to static JSON")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init", help="Sync SQLite DB and static JSON")
    sub.add_parser("summary", help="Show work packages and item status counts")
    p_pkg = sub.add_parser("package", help="Show items linked to a work package")
    p_pkg.add_argument("name", help="Work package id (e.g. diesel_heater, floor_rivet_holes)")
    sub.add_parser("shared", help="Show items shared across multiple work packages")
    sub.add_parser("pending", help="Show items still to buy")

    p_ord = sub.add_parser("mark-ordered", help="Mark items ordered by SKU or node id")
    p_ord.add_argument("keys", nargs="+", help="Item SKU(s) or node ID(s)")
    p_ord.add_argument("--date", default="2026-10-26", help="Order date (YYYY-MM-DD)")

    p_stat = sub.add_parser("set-status", help="Change item status (owned/ordered/planned/candidate/tbd)")
    p_stat.add_argument("key", help="Item ID or SKU")
    p_stat.add_argument("status", choices=VALID_ITEM_STATUSES)
    p_stat.add_argument("--date", default=None, help="Order date if status=ordered")

    p_add = sub.add_parser("add", help="Add or update a shopping item")
    p_add.add_argument("--id", default=None, help="Optional item:... id")
    p_add.add_argument("--name", required=True, help="Item name")
    p_add.add_argument("--packages", required=True, help="Comma-separated work packages (e.g. maxxfan,diesel_heater)")
    p_add.add_argument("--status", choices=VALID_ITEM_STATUSES, default="planned")
    p_add.add_argument("--qty", default="1 pc")
    p_add.add_argument("--supplier", default="")
    p_add.add_argument("--sku", default=None)
    p_add.add_argument("--url", default=None)
    p_add.add_argument("--date", default=None)
    p_add.add_argument("--notes", default="")
    p_add.add_argument("--price", type=float, default=None, help="Listed unit price in euros")

    p_rm = sub.add_parser("remove", help="Remove a shopping item by ID or SKU")
    p_rm.add_argument("key", help="Item ID or SKU")

    p_srv = sub.add_parser("serve", help="Serve blog HTML + read/write /api/graph endpoint")
    p_srv.add_argument("--port", type=int, default=8000)
    p_srv.add_argument("--bind", default="127.0.0.1")

    sub.add_parser("export-json", help="Dump bipartite graph as JSON")

    args = parser.parse_args()
    if args.cmd == "serve":
        ensure_synced(args.json, args.db).close()
        run_server(args.port, args.bind, args.json, args.db, DEFAULT_BUILD_HTML)
        return

    with ensure_synced(args.json, args.db) as conn:
        if args.cmd in (None, "init", "summary"):
            save_graph(load_graph_from_sqlite(conn), args.json, args.db)
            cmd_summary(conn)
        elif args.cmd == "package":
            cmd_package(conn, args.name)
        elif args.cmd == "shared":
            cmd_shared(conn)
        elif args.cmd == "pending":
            cmd_pending(conn)
        elif args.cmd == "mark-ordered":
            cmd_set_status(conn, args.keys, "ordered", args.date)
            save_graph(load_graph_from_sqlite(conn), args.json, args.db)
        elif args.cmd == "set-status":
            cmd_set_status(conn, [args.key], args.status, args.date)
            save_graph(load_graph_from_sqlite(conn), args.json, args.db)
        elif args.cmd == "add":
            pkgs = [p.strip() for p in args.packages.split(",") if p.strip()]
            cmd_add_item(
                conn,
                name=args.name,
                packages=pkgs,
                item_id=args.id,
                status=args.status,
                qty=args.qty,
                supplier=args.supplier,
                sku=args.sku,
                url=args.url,
                ordered_date=args.date,
                notes=args.notes,
                price_eur=args.price,
            )
            save_graph(load_graph_from_sqlite(conn), args.json, args.db)
        elif args.cmd == "remove":
            cmd_remove_item(conn, args.key)
            save_graph(load_graph_from_sqlite(conn), args.json, args.db)
        elif args.cmd == "export-json":
            print(json.dumps(load_graph_from_sqlite(conn), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
