#!/usr/bin/env python3
"""Browser-backed K-Rauta query helper.

K-Rauta blocks simple HTTP clients, but product/store pages and API calls work
from Chromium. This script uses Chrome DevTools Protocol directly so repeated
availability/search checks do not require ad hoc inline Python.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


BASE_URL = "https://www.k-rauta.fi"
DEFAULT_PORT = 9223
DEFAULT_STORES = ("F509", "F548")  # Lahdesjarvi, Palkane


class CdpError(RuntimeError):
    pass


@dataclass
class CdpClient:
    socket: socket.socket
    next_id: int = 0

    @classmethod
    def connect(cls, port: int) -> "CdpClient":
        targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list"))
        if not targets:
            raise CdpError("No Chromium DevTools targets found")
        ws_url = targets[0]["webSocketDebuggerUrl"]
        hostport, path = ws_url[5:].split("/", 1)
        path = "/" + path
        host, raw_port = hostport.split(":")

        sock = socket.create_connection((host, int(raw_port)))
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {hostport}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        sock.sendall(request.encode("utf-8"))
        response = sock.recv(4096)
        if b"101" not in response.split(b"\r\n", 1)[0]:
            raise CdpError(f"DevTools websocket handshake failed: {response[:200]!r}")
        return cls(sock)

    def send(self, method: str, params: dict[str, Any] | None = None) -> int:
        self.next_id += 1
        payload = json.dumps(
            {"id": self.next_id, "method": method, "params": params or {}}
        ).encode("utf-8")

        header = bytearray([0x81])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))

        mask = os.urandom(4)
        header.extend(mask)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.socket.sendall(header + masked)
        return self.next_id

    def recv(self, timeout: float = 10) -> dict[str, Any]:
        self.socket.settimeout(timeout)
        first = self.socket.recv(2)
        if not first:
            raise EOFError("DevTools socket closed")

        byte_1, byte_2 = first
        opcode = byte_1 & 0x0F
        masked = byte_2 & 0x80
        length = byte_2 & 0x7F
        if length == 126:
            length = struct.unpack("!H", self.socket.recv(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self.socket.recv(8))[0]

        mask = self.socket.recv(4) if masked else b""
        payload = b""
        while len(payload) < length:
            payload += self.socket.recv(length - len(payload))
        if masked:
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))

        if opcode == 8:
            raise EOFError("DevTools socket closed")
        if opcode != 1:
            return {}
        return json.loads(payload.decode("utf-8"))

    def call(
        self, method: str, params: dict[str, Any] | None = None, timeout: float = 30
    ) -> dict[str, Any]:
        message_id = self.send(method, params)
        deadline = time.time() + timeout
        while time.time() < deadline:
            message = self.recv(max(1, deadline - time.time()))
            if message.get("id") == message_id:
                if "error" in message:
                    raise CdpError(json.dumps(message["error"], indent=2))
                return message
        raise TimeoutError(method)

    def eval(
        self, expression: str, *, await_promise: bool = False, timeout: float = 30
    ) -> Any:
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": True,
            },
            timeout=timeout,
        )
        value = result["result"]["result"]
        if value.get("subtype") == "error":
            raise CdpError(json.dumps(value, indent=2))
        return value.get("value")

    def navigate(self, url: str, wait_seconds: float = 5) -> None:
        self.call("Page.enable")
        self.call("Runtime.enable")
        self.call("Page.navigate", {"url": url})
        time.sleep(wait_seconds)


def ensure_browser(port: int) -> subprocess.Popen[str] | None:
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
        return None
    except Exception:
        pass

    process = subprocess.Popen(
        [
            "chromium",
            "--headless",
            "--disable-gpu",
            f"--remote-debugging-port={port}",
            "--user-data-dir=/tmp/krauta-cdp",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1)
            return process
        except Exception:
            time.sleep(0.2)
    raise CdpError("Timed out waiting for Chromium DevTools")


def normalize_store_slug(slug_or_url: str) -> str:
    if slug_or_url.startswith("http"):
        return slug_or_url.rstrip("/").split("/")[-1]
    return slug_or_url.strip("/")


def command_store_id(client: CdpClient, args: argparse.Namespace) -> None:
    slug = normalize_store_slug(args.store)
    client.navigate(f"{BASE_URL}/myymalat/{slug}", wait_seconds=args.wait)
    value = client.eval(
        r"""
        (() => {
          const html = document.documentElement.innerHTML;
          const match = html.match(/"storeId":"([^"]+)","storeName":"([^"]+)"/);
          return {
            title: document.title,
            url: location.href,
            storeId: match && match[1],
            storeName: match && match[2]
          };
        })()
        """
    )
    print(json.dumps(value, ensure_ascii=False, indent=2))


def command_availability(client: CdpClient, args: argparse.Namespace) -> None:
    eans = [ean.strip() for ean in args.eans if ean.strip()]
    stores = [store.strip() for store in args.stores if store.strip()]
    client.navigate(BASE_URL, wait_seconds=args.wait)
    expression = f"""
    (async () => {{
      const eans = {json.dumps(eans)};
      const stores = {json.dumps(stores)};
      const response = await fetch('/api/availability', {{
        method: 'POST',
        headers: {{'content-type': 'application/json'}},
        body: JSON.stringify({{eans}})
      }});
      const data = await response.json();
      const out = {{}};
      for (const ean of eans) {{
        const rows = (data[ean] && data[ean].storeAvailabilities) || [];
        out[ean] = {{
          selectedStores: Object.fromEntries(stores.map(id => [
            id,
            rows.find(row => row.store.id === id) || null
          ])),
          availableStores: rows
            .filter(row => row.availability.status === 'AVAILABLE')
            .map(row => ({{
              id: row.store.id,
              name: row.store.name,
              quantity: row.quantity,
              status: row.availability.status,
              info: row.availability.info || null,
              pickupDisabled: row.restrictions.pickupDisabled
            }}))
        }};
      }}
      return out;
    }})()
    """
    print(json.dumps(client.eval(expression, await_promise=True), ensure_ascii=False, indent=2))


def command_search(client: CdpClient, args: argparse.Namespace) -> None:
    query = urllib.parse.quote(args.query)
    client.navigate(f"{BASE_URL}/etsi?query={query}", wait_seconds=args.wait)
    expression = r"""
    (() => {
      const html = document.documentElement.innerHTML;
      const match = html.match(/"fetchedProducts":(\{.*?\}),"punchout"/);
      if (!match) {
        return {title: document.title, products: [], parseError: "fetchedProducts not found"};
      }
      const products = Object.values(JSON.parse(match[1]));
      return {
        title: document.title,
        products: products.slice(0, 40).map(product => ({
          ean: String(product.ean),
          name: product.name,
          brand: product.brand,
          productId: product.productId
        }))
      };
    })()
    """
    print(json.dumps(client.eval(expression), ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--wait", type=float, default=5.0)

    subparsers = parser.add_subparsers(dest="command", required=True)

    store_id = subparsers.add_parser("store-id", help="Resolve K-Rauta store slug/URL")
    store_id.add_argument("store")
    store_id.set_defaults(func=command_store_id)

    availability = subparsers.add_parser("availability", help="Check EAN availability")
    availability.add_argument("eans", nargs="+")
    availability.add_argument("--stores", nargs="+", default=list(DEFAULT_STORES))
    availability.set_defaults(func=command_availability)

    search = subparsers.add_parser("search", help="Search products and print EANs")
    search.add_argument("query")
    search.set_defaults(func=command_search)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    browser = ensure_browser(args.port)
    try:
        client = CdpClient.connect(args.port)
        args.func(client, args)
    finally:
        if browser is not None:
            browser.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
