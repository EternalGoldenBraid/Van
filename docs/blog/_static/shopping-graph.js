(() => {
  const STATUS_META = {
    owned: { label: "Owned", color: "var(--stove-green)", bg: "var(--stove-green-bg)" },
    bought: { label: "Bought", color: "var(--stove-green)", bg: "var(--stove-green-bg)" },
    ordered: { label: "Ordered", color: "var(--stove-blue)", bg: "var(--stove-blue-bg)" },
    planned: { label: "Planned", color: "var(--stove-amber)", bg: "var(--stove-amber-bg)" },
    candidate: { label: "Candidate", color: "var(--stove-amber)", bg: "var(--stove-amber-bg)" },
    tbd: { label: "TBD", color: "var(--stove-neutral)", bg: "var(--stove-neutral-bg)" },
  };
  const STATUS_ORDER = ["planned", "candidate", "tbd", "ordered", "bought", "owned"];
  const GH_REPO = "EternalGoldenBraid/Van";
  const GH_PATH = "docs/blog/_static/shopping_graph.json";
  const GH_TOKEN_KEY = "van_shopping_graph_gh_token";

  function getSiteRootPrefix() {
    const scriptEl = document.querySelector('script[src*="shopping-graph.js"]');
    if (scriptEl) {
      const src = scriptEl.getAttribute("src") || "";
      const idx = src.indexOf("_static/shopping-graph.js");
      if (idx >= 0) return src.slice(0, idx);
    }
    return "";
  }

  function docHref(docPath) {
    if (!docPath) return null;
    const rel = docPath.replace(/^docs\/blog\//, "").replace(/\.md$/, ".html");
    return getSiteRootPrefix() + rel;
  }

  function slugify(str) {
    return (
      String(str || "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "")
        .slice(0, 48) || "item"
    );
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function todayIso() {
    return new Date().toISOString().slice(0, 10);
  }

  async function initShoppingGraph(root) {
    const fixedWp = root.dataset.workPackage || null;
    const sitePrefix = getSiteRootPrefix();
    const jsonUrl = root.dataset.graphUrl || `${sitePrefix}_static/shopping_graph.json`;
    let data;
    let localApiAvailable = false;

    try {
      const apiResp = await fetch("/api/graph", { method: "GET" });
      if (apiResp.ok && (apiResp.headers.get("content-type") || "").includes("json")) {
        data = await apiResp.json();
        localApiAvailable = true;
      }
    } catch (_) {
      // Fallback to static JSON
    }

    if (!data) {
      try {
        const resp = await fetch(jsonUrl);
        data = await resp.json();
      } catch (err) {
        root.innerHTML = `<p>Could not load shopping graph data (${escapeHtml(err.message)}).</p>`;
        return;
      }
    }

    let state = {
      wpFilter: fixedWp || "all",
      statusFilter: "all",
      selectedItemId: null,
      saveMsg: localApiAvailable
        ? "Connected to local DB (edits save automatically)"
        : "Static mode (click 'GitHub Sync' to commit edits to repo)",
    };

    const workPackages = () => data.nodes.filter((n) => n.node_type === "work_package");
    const shoppingItems = () => data.nodes.filter((n) => n.node_type === "shopping_item");
    const edges = () => data.edges || [];

    async function persistGraph(commitMessage) {
      if (localApiAvailable) {
        try {
          state.saveMsg = "Saving to local DB…";
          updateSaveStatus();
          const resp = await fetch("/api/graph", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
          });
          const res = await resp.json();
          if (res.ok && res.graph) {
            data = res.graph;
            state.saveMsg = "Saved to local SQLite & JSON (" + new Date().toLocaleTimeString() + ")";
          } else {
            state.saveMsg = "Save error: " + (res.error || resp.statusText);
          }
        } catch (err) {
          state.saveMsg = "Local save failed: " + err.message;
        }
        updateSaveStatus();
        render();
        return;
      }

      const token = localStorage.getItem(GH_TOKEN_KEY);
      if (!token) {
        state.saveMsg = "Updated in browser — click 'GitHub Sync' to commit to GitHub";
        updateSaveStatus();
        render();
        return;
      }

      try {
        state.saveMsg = "Committing to GitHub…";
        updateSaveStatus();
        const apiUrl = `https://api.github.com/repos/${GH_REPO}/contents/${GH_PATH}`;
        const curResp = await fetch(apiUrl, {
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/vnd.github+json",
          },
        });
        if (!curResp.ok) throw new Error(`GitHub GET ${curResp.status}`);
        const curFile = await curResp.json();
        const jsonText = JSON.stringify(data, null, 2) + "\n";
        const b64 = btoa(unescape(encodeURIComponent(jsonText)));

        const putResp = await fetch(apiUrl, {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/vnd.github+json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: commitMessage || "docs: update shopping_graph.json",
            content: b64,
            sha: curFile.sha,
          }),
        });
        if (!putResp.ok) throw new Error(`GitHub PUT ${putResp.status}`);
        state.saveMsg = "Committed to GitHub (" + new Date().toLocaleTimeString() + ")";
      } catch (err) {
        state.saveMsg = "GitHub commit failed: " + err.message;
      }
      updateSaveStatus();
      render();
    }

    const wpButtonsHtml = [
      `<button type="button" class="sg-pill is-active" data-wp="all">All packages</button>`,
      ...workPackages().map((wp) => {
        const shortLabel = wp.name.replace(/\s*\(.*\)$/, "");
        return `<button type="button" class="sg-pill" data-wp="${escapeHtml(wp.id)}">${escapeHtml(shortLabel)}</button>`;
      }),
    ].join("");

    const wpCheckboxesHtml = workPackages()
      .map((wp) => {
        const shortLabel = wp.name.replace(/\s*\(.*\)$/, "");
        return `<label class="sg-wp-check"><input type="checkbox" name="wp" value="${escapeHtml(wp.id)}"> ${escapeHtml(shortLabel)}</label>`;
      })
      .join("");

    const wpFilterRowHtml = fixedWp
      ? ""
      : `
        <div class="sg-filter-row">
          <span class="sg-filter-label">Work package:</span>
          <div class="sg-filters" role="group" aria-label="Filter by work package">
            ${wpButtonsHtml}
          </div>
        </div>
      `;

    const fullGraphLinkHtml = fixedWp
      ? `<a class="sg-btn" href="${escapeHtml(sitePrefix + "shopping-graph.html")}">Full graph →</a>`
      : "";

    const canvasBlockHtml = fixedWp
      ? `
        <details class="sg-graph-details">
          <summary class="sg-add-summary">Show bipartite graph connections</summary>
          <div class="sg-canvas-wrap">
            <svg class="sg-svg" role="img" aria-label="Bipartite graph of work packages and shopping items"></svg>
          </div>
        </details>
      `
      : `
        <div class="sg-canvas-wrap">
          <svg class="sg-svg" role="img" aria-label="Bipartite graph of work packages and shopping items"></svg>
        </div>
      `;

    root.innerHTML = `
      <div class="sg-toolbar">
        ${wpFilterRowHtml}
        <div class="sg-filter-row">
          <span class="sg-filter-label">Status:</span>
          <div class="sg-filters" role="group" aria-label="Filter by status">
            <button type="button" class="sg-status-pill is-active" data-status="all">All</button>
            <button type="button" class="sg-status-pill" data-status="todo">To buy</button>
            <button type="button" class="sg-status-pill" data-status="ordered">Ordered</button>
            <button type="button" class="sg-status-pill" data-status="owned">Bought / Owned</button>
          </div>
          <div class="sg-actions-right">
            ${fullGraphLinkHtml}
            <button type="button" class="sg-btn sg-gh-btn" ${localApiAvailable ? "hidden" : ""}>GitHub Sync</button>
          </div>
        </div>
        <details class="sg-add-details">
          <summary class="sg-add-summary">+ Add new shopping item</summary>
          <form class="sg-add-form">
            <div class="sg-add-grid">
              <input type="text" name="name" required placeholder="Item name (e.g. Sikaflex-221)" class="sg-input">
              <select name="status" class="sg-select">
                <option value="planned">Planned</option>
                <option value="candidate">Candidate</option>
                <option value="tbd">TBD</option>
                <option value="ordered">Ordered</option>
                <option value="bought">Bought</option>
                <option value="owned">Owned</option>
              </select>
              <input type="text" name="qty" placeholder="Qty (e.g. 1 pc)" value="1 pc" class="sg-input">
              <input type="text" name="supplier" placeholder="Supplier (e.g. Puuilo)" class="sg-input">
              <input type="text" name="sku" placeholder="SKU / EAN (optional)" class="sg-input">
              <input type="url" name="url" placeholder="Product URL (optional)" class="sg-input">
            </div>
            <div class="sg-wp-checks">
              <span class="sg-filter-label">Work packages:</span>
              ${wpCheckboxesHtml}
            </div>
            <div class="sg-add-submit-row">
              <input type="text" name="notes" placeholder="Notes (optional)" class="sg-input sg-input-wide">
              <button type="submit" class="sg-btn sg-btn-primary">Add item</button>
            </div>
          </form>
        </details>
        <div class="sg-save-bar">
          <span class="sg-save-msg"></span>
        </div>
      </div>
      <div class="sg-item-editor" hidden></div>
      ${fixedWp ? '<div class="sg-detail"></div>' + canvasBlockHtml : canvasBlockHtml + '<div class="sg-detail"></div>'}
    `;

    const svg = root.querySelector(".sg-svg");
    const editorEl = root.querySelector(".sg-item-editor");
    const detail = root.querySelector(".sg-detail");
    const saveMsgEl = root.querySelector(".sg-save-msg");
    const addDetails = root.querySelector(".sg-add-details");
    const addForm = root.querySelector(".sg-add-form");
    const ghBtn = root.querySelector(".sg-gh-btn");
    const wpButtons = Array.from(root.querySelectorAll("[data-wp]"));
    const statusButtons = Array.from(root.querySelectorAll("[data-status]"));

    function updateSaveStatus() {
      saveMsgEl.textContent = state.saveMsg;
    }
    updateSaveStatus();

    addDetails.addEventListener("toggle", () => {
      if (addDetails.open && state.wpFilter !== "all") {
        addForm.querySelectorAll('input[name="wp"]').forEach((cb) => {
          cb.checked = cb.value === state.wpFilter;
        });
      }
    });

    ghBtn.addEventListener("click", () => {
      const current = localStorage.getItem(GH_TOKEN_KEY) || "";
      const next = window.prompt(
        "Enter a GitHub Personal Access Token (contents:write on EternalGoldenBraid/Van) to commit edits directly from the browser. Leave blank to clear:",
        current
      );
      if (next === null) return;
      if (next.trim()) {
        localStorage.setItem(GH_TOKEN_KEY, next.trim());
        state.saveMsg = "GitHub token saved in browser localStorage.";
      } else {
        localStorage.removeItem(GH_TOKEN_KEY);
        state.saveMsg = "GitHub token cleared.";
      }
      updateSaveStatus();
    });

    addForm.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(addForm);
      const name = String(fd.get("name") || "").trim();
      if (!name) return;
      const checkedWps = fd.getAll("wp").map(String);
      const targetWps =
        checkedWps.length > 0
          ? checkedWps
          : state.wpFilter !== "all"
          ? [state.wpFilter]
          : [workPackages()[0].id];

      const status = String(fd.get("status") || "planned");
      const newId = `item:${slugify(name)}_${Date.now().toString(36).slice(-4)}`;
      const newNode = {
        id: newId,
        node_type: "shopping_item",
        name,
        status,
        sku: String(fd.get("sku") || "").trim() || null,
        supplier: String(fd.get("supplier") || "").trim() || null,
        qty: String(fd.get("qty") || "1 pc").trim(),
        url: String(fd.get("url") || "").trim() || null,
        ordered_date: status === "ordered" || status === "bought" ? todayIso() : null,
        doc_path: null,
        notes: String(fd.get("notes") || "").trim() || null,
      };
      data.nodes.push(newNode);
      for (const wpId of targetWps) {
        data.edges.push({
          work_package_id: wpId,
          shopping_item_id: newId,
          role: "required",
          notes: newNode.notes,
        });
      }
      addForm.reset();
      addDetails.open = false;
      state.selectedItemId = newId;
      await persistGraph(`docs: add shopping item '${name}'`);
    });

    function setWpFilter(wpId) {
      state.wpFilter = wpId;
      wpButtons.forEach((b) => {
        b.classList.toggle("is-active", b.getAttribute("data-wp") === wpId);
      });
      render();
    }

    function itemMatchesStatus(item) {
      if (state.statusFilter === "todo") {
        return ["planned", "candidate", "tbd"].includes(item.status);
      }
      if (state.statusFilter === "ordered") return item.status === "ordered";
      if (state.statusFilter === "owned") return ["owned", "bought"].includes(item.status);
      return true;
    }

    function renderItemEditor() {
      if (!state.selectedItemId) {
        editorEl.hidden = true;
        editorEl.innerHTML = "";
        return;
      }
      const item = shoppingItems().find((i) => i.id === state.selectedItemId);
      if (!item) {
        state.selectedItemId = null;
        editorEl.hidden = true;
        editorEl.innerHTML = "";
        return;
      }

      editorEl.hidden = false;
      const linkedWpIds = new Set(
        edges()
          .filter((e) => e.shopping_item_id === item.id)
          .map((e) => e.work_package_id)
      );

      const statusBtns = STATUS_ORDER.map((st) => {
        const meta = STATUS_META[st] || STATUS_META.tbd;
        const active = item.status === st ? "is-active" : "";
        return `<button type="button" class="sg-status-quick sg-badge-${escapeHtml(st)} ${active}" data-quick-status="${escapeHtml(st)}">${escapeHtml(meta.label)}</button>`;
      }).join("");

      const wpChecks = workPackages()
        .map((wp) => {
          const shortLabel = wp.name.replace(/\s*\(.*\)$/, "");
          const checked = linkedWpIds.has(wp.id) ? "checked" : "";
          return `<label class="sg-wp-check"><input type="checkbox" name="edit_wp" value="${escapeHtml(wp.id)}" ${checked}> ${escapeHtml(shortLabel)}</label>`;
        })
        .join("");

      editorEl.innerHTML = `
        <div class="sg-editor-header">
          <div>
            <strong>Edit item:</strong> ${escapeHtml(item.name)}
            ${item.sku ? `<code>${escapeHtml(item.sku)}</code>` : ""}
          </div>
          <button type="button" class="sg-btn sg-editor-close" aria-label="Close item editor">Close ✕</button>
        </div>
        <div class="sg-editor-status-row">
          <span class="sg-filter-label">Mark status:</span>
          <div class="sg-filters">${statusBtns}</div>
        </div>
        <details class="sg-edit-details">
          <summary class="sg-add-summary">Edit details & work packages</summary>
          <form class="sg-edit-form">
            <div class="sg-add-grid">
              <input type="text" name="name" value="${escapeHtml(item.name)}" required class="sg-input" placeholder="Name">
              <input type="text" name="qty" value="${escapeHtml(item.qty || "")}" class="sg-input" placeholder="Qty">
              <input type="text" name="supplier" value="${escapeHtml(item.supplier || "")}" class="sg-input" placeholder="Supplier">
              <input type="text" name="sku" value="${escapeHtml(item.sku || "")}" class="sg-input" placeholder="SKU">
              <input type="url" name="url" value="${escapeHtml(item.url || "")}" class="sg-input" placeholder="URL">
            </div>
            <div class="sg-wp-checks">
              <span class="sg-filter-label">Work packages:</span>
              ${wpChecks}
            </div>
            <div class="sg-add-submit-row">
              <input type="text" name="notes" value="${escapeHtml(item.notes || "")}" class="sg-input sg-input-wide" placeholder="Notes">
              <button type="submit" class="sg-btn sg-btn-primary">Save changes</button>
              <button type="button" class="sg-btn sg-btn-danger" data-delete-item="${escapeHtml(item.id)}">Delete item</button>
            </div>
          </form>
        </details>
      `;

      editorEl.querySelector(".sg-editor-close").addEventListener("click", () => {
        state.selectedItemId = null;
        render();
      });

      editorEl.querySelectorAll("[data-quick-status]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const newStatus = btn.getAttribute("data-quick-status");
          item.status = newStatus;
          if ((newStatus === "ordered" || newStatus === "bought") && !item.ordered_date) {
            item.ordered_date = todayIso();
          }
          await persistGraph(`docs: mark '${item.name}' as ${newStatus}`);
        });
      });

      const editForm = editorEl.querySelector(".sg-edit-form");
      editForm.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const fd = new FormData(editForm);
        item.name = String(fd.get("name") || item.name).trim();
        item.qty = String(fd.get("qty") || "").trim() || null;
        item.supplier = String(fd.get("supplier") || "").trim() || null;
        item.sku = String(fd.get("sku") || "").trim() || null;
        item.url = String(fd.get("url") || "").trim() || null;
        item.notes = String(fd.get("notes") || "").trim() || null;

        const chosenWps = fd.getAll("edit_wp").map(String);
        data.edges = data.edges.filter((e) => e.shopping_item_id !== item.id);
        for (const wpId of chosenWps) {
          data.edges.push({
            work_package_id: wpId,
            shopping_item_id: item.id,
            role: "required",
            notes: item.notes,
          });
        }
        await persistGraph(`docs: update shopping item '${item.name}'`);
      });

      const delBtn = editorEl.querySelector("[data-delete-item]");
      delBtn.addEventListener("click", async () => {
        const name = item.name;
        data.nodes = data.nodes.filter((n) => n.id !== item.id);
        data.edges = data.edges.filter((e) => e.shopping_item_id !== item.id);
        state.selectedItemId = null;
        await persistGraph(`docs: remove shopping item '${name}'`);
      });
    }

    function render() {
      renderItemEditor();

      const wps = workPackages();
      const items = shoppingItems();
      const allEdges = edges();

      const degByItem = new Map();
      for (const e of allEdges) {
        degByItem.set(e.shopping_item_id, (degByItem.get(e.shopping_item_id) || 0) + 1);
      }

      const relevantEdges = allEdges.filter(
        (e) => state.wpFilter === "all" || e.work_package_id === state.wpFilter
      );
      const relevantItemIds = new Set(relevantEdges.map((e) => e.shopping_item_id));
      const visibleItems = items.filter(
        (item) => relevantItemIds.has(item.id) && itemMatchesStatus(item)
      );
      const visibleItemIds = new Set(visibleItems.map((i) => i.id));
      const visibleEdges = allEdges.filter((e) => visibleItemIds.has(e.shopping_item_id));

      const leftX = 16;
      const leftW = 245;
      const rightX = 410;
      const rightW = 450;
      const width = 876;

      const wpRowH = 52;
      const itemRowH = 32;
      const padTop = 34;
      const height = Math.max(
        padTop + wps.length * wpRowH + 20,
        padTop + Math.max(visibleItems.length, 1) * itemRowH + 20,
        280
      );

      const wpPos = new Map();
      const wpSpan = Math.max(height - padTop - 20, wpRowH * wps.length);
      const wpStep = wpSpan / Math.max(wps.length, 1);
      wps.forEach((wp, idx) => {
        wpPos.set(wp.id, {
          x: leftX,
          y: padTop + idx * wpStep + (wpStep - 38) / 2,
          cy: padTop + idx * wpStep + wpStep / 2,
        });
      });

      const itemPos = new Map();
      visibleItems.forEach((item, idx) => {
        itemPos.set(item.id, {
          x: rightX,
          y: padTop + idx * itemRowH,
          cy: padTop + idx * itemRowH + 13,
        });
      });

      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

      const parts = [];
      parts.push(
        `<text x="${leftX}" y="20" class="sg-col-title">WORK PACKAGES (click to filter)</text>`,
        `<text x="${rightX}" y="20" class="sg-col-title">SHOPPING ITEMS (${visibleItems.length} — click item to edit)</text>`
      );

      for (const e of visibleEdges) {
        const p1 = wpPos.get(e.work_package_id);
        const p2 = itemPos.get(e.shopping_item_id);
        if (!p1 || !p2) continue;
        const x1 = p1.x + leftW;
        const y1 = p1.cy;
        const x2 = p2.x;
        const y2 = p2.cy;
        const cx1 = x1 + (x2 - x1) * 0.45;
        const cx2 = x1 + (x2 - x1) * 0.55;
        const item = items.find((i) => i.id === e.shopping_item_id);
        const isItemSelected = state.selectedItemId && e.shopping_item_id === state.selectedItemId;
        const isWpSelected = state.wpFilter !== "all" && e.work_package_id === state.wpFilter;
        const isHi = isItemSelected || isWpSelected;
        const isDim =
          (state.selectedItemId && !isItemSelected) ||
          (!state.selectedItemId && state.wpFilter !== "all" && !isWpSelected);
        const cls = [
          "sg-edge",
          `sg-edge-${item ? item.status : "tbd"}`,
          isHi ? "is-highlight" : "",
          isDim ? "is-dim" : "",
        ]
          .filter(Boolean)
          .join(" ");
        parts.push(`<path d="M ${x1} ${y1} C ${cx1} ${y1}, ${cx2} ${y2}, ${x2} ${y2}" class="${cls}" />`);
      }

      for (const wp of wps) {
        const pos = wpPos.get(wp.id);
        const isSel = state.wpFilter === wp.id;
        const isLinkedToSelItem =
          state.selectedItemId &&
          allEdges.some((e) => e.work_package_id === wp.id && e.shopping_item_id === state.selectedItemId);
        const isDim =
          (state.selectedItemId && !isLinkedToSelItem) ||
          (!state.selectedItemId && state.wpFilter !== "all" && !isSel);
        const totalForWp = allEdges.filter((e) => e.work_package_id === wp.id).length;
        const cls = [
          "sg-node",
          "sg-node-wp",
          isSel || isLinkedToSelItem ? "is-selected" : "",
          isDim ? "is-dim" : "",
        ]
          .filter(Boolean)
          .join(" ");
        const shortTitle = wp.name.replace(/\s*\(.*\)$/, "");
        parts.push(`
          <g class="${cls}" data-wp-node="${escapeHtml(wp.id)}" tabindex="0" role="button" aria-label="Filter by ${escapeHtml(wp.name)}">
            <rect x="${pos.x}" y="${pos.y}" width="${leftW}" height="38" rx="6" />
            <text x="${pos.x + 10}" y="${pos.y + 16}" class="sg-node-title">${escapeHtml(shortTitle)}</text>
            <text x="${pos.x + 10}" y="${pos.y + 30}" class="sg-node-sub">${escapeHtml(wp.status)} · ${totalForWp} items</text>
            <circle cx="${pos.x + leftW}" cy="${pos.cy}" r="4" class="sg-port" />
          </g>
        `);
      }

      for (const item of visibleItems) {
        const pos = itemPos.get(item.id);
        const deg = degByItem.get(item.id) || 0;
        const isSel = state.selectedItemId === item.id;
        const isDim = state.selectedItemId && !isSel;
        const cls = [
          "sg-node",
          "sg-node-item",
          `sg-status-${item.status}`,
          isSel ? "is-selected" : "",
          isDim ? "is-dim" : "",
        ]
          .filter(Boolean)
          .join(" ");
        const maxChars = 48;
        const label = item.name.length > maxChars ? item.name.slice(0, maxChars - 1) + "…" : item.name;
        const badge = (STATUS_META[item.status] || STATUS_META.tbd).label;
        parts.push(`
          <g class="${cls}" data-item-node="${escapeHtml(item.id)}" tabindex="0" role="button" aria-label="Edit ${escapeHtml(item.name)}">
            <rect x="${pos.x}" y="${pos.y}" width="${rightW}" height="26" rx="5" />
            <circle cx="${pos.x}" cy="${pos.cy}" r="3.5" class="sg-port" />
            <text x="${pos.x + 10}" y="${pos.y + 17}" class="sg-item-title">${escapeHtml(label)}</text>
            <text x="${pos.x + rightW - 8}" y="${pos.y + 17}" text-anchor="end" class="sg-item-meta">${escapeHtml(badge)}${deg > 1 ? ` · ${deg}×` : ""}</text>
          </g>
        `);
      }

      svg.innerHTML = parts.join("\n");

      svg.querySelectorAll("[data-wp-node]").forEach((el) => {
        const id = el.getAttribute("data-wp-node");
        const toggle = () => setWpFilter(state.wpFilter === id ? "all" : id);
        el.addEventListener("click", toggle);
        el.addEventListener("keydown", (ev) => {
          if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            toggle();
          }
        });
      });

      svg.querySelectorAll("[data-item-node]").forEach((el) => {
        const id = el.getAttribute("data-item-node");
        const selectItem = () => {
          state.selectedItemId = state.selectedItemId === id ? null : id;
          render();
          if (state.selectedItemId) {
            editorEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
          }
        };
        el.addEventListener("click", selectItem);
        el.addEventListener("keydown", (ev) => {
          if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            selectItem();
          }
        });
      });

      renderDetail(visibleItems);
    }

    function renderDetail(visibleItems) {
      const wps = workPackages();
      const allEdges = edges();
      const selWp = wps.find((w) => w.id === state.wpFilter);
      const title = selWp ? `${selWp.name}` : "All work packages";
      const href = selWp ? docHref(selWp.doc_path) : null;
      const wpLinkHtml = href ? ` · <a href="${escapeHtml(href)}">Open work package →</a>` : "";

      const rowsHtml = visibleItems
        .map((item) => {
          const itemEdges = allEdges.filter((e) => e.shopping_item_id === item.id);
          const pkgLinks = itemEdges
            .map((e) => {
              const wp = wps.find((w) => w.id === e.work_package_id);
              if (!wp) return "";
              const h = docHref(wp.doc_path);
              const shortName = wp.id.replace(/^wp:/, "");
              return h ? `<a href="${escapeHtml(h)}">${escapeHtml(shortName)}</a>` : escapeHtml(shortName);
            })
            .join(", ");
          const nameCell = item.url
            ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener">${escapeHtml(item.name)}</a>`
            : escapeHtml(item.name);
          const skuPart = item.sku ? ` <code>${escapeHtml(item.sku)}</code>` : "";
          const optionsHtml = STATUS_ORDER.map((st) => {
            const lbl = STATUS_META[st].label;
            const sel = item.status === st ? "selected" : "";
            return `<option value="${st}" ${sel}>${lbl}</option>`;
          }).join("");
          const isRowSel = state.selectedItemId === item.id ? "is-selected-row" : "";
          return `
            <tr class="${isRowSel}" data-item-row="${escapeHtml(item.id)}">
              <td>
                <select class="sg-status-select sg-badge-${escapeHtml(item.status)}" data-status-for="${escapeHtml(item.id)}" aria-label="Status for ${escapeHtml(item.name)}">
                  ${optionsHtml}
                </select>
              </td>
              <td>
                <button type="button" class="sg-item-link" data-edit-item="${escapeHtml(item.id)}">${escapeHtml(item.name)}</button>${skuPart}
                ${item.url ? ` <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener" title="Open product link">↗</a>` : ""}
              </td>
              <td>${escapeHtml(item.qty || "")}</td>
              <td>${escapeHtml(item.supplier || "")}</td>
              <td>${pkgLinks}</td>
              <td>
                <button type="button" class="sg-rm-btn" data-remove-id="${escapeHtml(item.id)}" title="Remove item" aria-label="Remove ${escapeHtml(item.name)}">✕</button>
              </td>
            </tr>
          `;
        })
        .join("");

      detail.innerHTML = `
        <p class="sg-summary-line"><strong>${escapeHtml(title)}</strong> — ${visibleItems.length} items${wpLinkHtml}</p>
        <div class="table-wrapper">
          <table class="sg-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Item / SKU (click to edit)</th>
                <th>Qty</th>
                <th>Supplier</th>
                <th>Used in</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml || '<tr><td colspan="6">No matching items.</td></tr>'}
            </tbody>
          </table>
        </div>
      `;

      detail.querySelectorAll("[data-edit-item]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const itemId = btn.getAttribute("data-edit-item");
          state.selectedItemId = state.selectedItemId === itemId ? null : itemId;
          render();
          if (state.selectedItemId) {
            editorEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
          }
        });
      });

      detail.querySelectorAll("[data-status-for]").forEach((sel) => {
        sel.addEventListener("change", async () => {
          const itemId = sel.getAttribute("data-status-for");
          const newStatus = sel.value;
          const target = data.nodes.find((n) => n.id === itemId);
          if (!target) return;
          target.status = newStatus;
          if ((newStatus === "ordered" || newStatus === "bought") && !target.ordered_date) {
            target.ordered_date = todayIso();
          }
          await persistGraph(`docs: set ${target.name} status to ${newStatus}`);
        });
      });

      detail.querySelectorAll("[data-remove-id]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const itemId = btn.getAttribute("data-remove-id");
          const target = data.nodes.find((n) => n.id === itemId);
          if (!target) return;
          data.nodes = data.nodes.filter((n) => n.id !== itemId);
          data.edges = data.edges.filter((e) => e.shopping_item_id !== itemId);
          if (state.selectedItemId === itemId) state.selectedItemId = null;
          await persistGraph(`docs: remove shopping item '${target.name}'`);
        });
      });
    }

    wpButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        setWpFilter(btn.getAttribute("data-wp") || "all");
      });
    });

    statusButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        statusButtons.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        state.statusFilter = btn.getAttribute("data-status") || "all";
        render();
      });
    });

    render();
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".js-shopping-graph").forEach((el) => {
      initShoppingGraph(el);
    });
  });
})();
