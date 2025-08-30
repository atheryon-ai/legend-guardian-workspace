(function () {
  const $ = (id) => document.getElementById(id);
  const apiKeyEl = $("apiKey");
  const saveKeyBtn = $("saveKey");
  const saveStatus = $("saveStatus");
  const checkHealthBtn = $("checkHealth");
  const healthOut = $("healthOut");
  const projectIdEl = $("projectId");
  const workspaceIdEl = $("workspaceId");
  const promptEl = $("prompt");
  const promptErr = $("promptErr");
  const projectIdErr = $("projectIdErr");
  const workspaceIdErr = $("workspaceIdErr");
  const runIntentBtn = $("runIntent");
  const copyCurlBtn = $("copyCurl");
  const intentStatus = $("intentStatus");
  const planOut = $("planOut");
  const logsOut = $("logsOut");
  const artifactsOut = $("artifactsOut");
  const rawOut = $("rawOut");
  const schemaOut = $("schemaOut");
  const openSettings = $("openSettings");
  const closeSettings = $("closeSettings");
  const drawer = $("settings");
  const backdrop = $("settingsBackdrop");
  const defaultProjectIdEl = $("defaultProjectId");
  const defaultWorkspaceIdEl = $("defaultWorkspaceId");
  const intentForm = $("intentForm");
  let restoreFocusEl = null;
  let trapHandler = null;

  // Load persisted values
  apiKeyEl.value = localStorage.getItem("lg_api_key") || "";
  const savedProj = localStorage.getItem("lg_project_id") || "";
  const savedWs = localStorage.getItem("lg_workspace_id") || "";
  projectIdEl.value = savedProj;
  workspaceIdEl.value = savedWs;
  defaultProjectIdEl.value = savedProj;
  defaultWorkspaceIdEl.value = savedWs;

  saveKeyBtn.addEventListener("click", () => {
    localStorage.setItem("lg_api_key", apiKeyEl.value.trim());
    localStorage.setItem("lg_project_id", defaultProjectIdEl.value.trim());
    localStorage.setItem("lg_workspace_id", defaultWorkspaceIdEl.value.trim());
    // Sync into current form if empty
    if (!projectIdEl.value) projectIdEl.value = defaultProjectIdEl.value.trim();
    if (!workspaceIdEl.value) workspaceIdEl.value = defaultWorkspaceIdEl.value.trim();
    saveStatus.textContent = "Saved";
    setTimeout(() => (saveStatus.textContent = ""), 1200);
  });

  // Settings drawer
  function openDrawer() {
    restoreFocusEl = document.activeElement;
    drawer.classList.add("open");
    drawer.setAttribute("aria-hidden", "false");
    backdrop.hidden = false;
    // Focus first control
    apiKeyEl.focus();
    // Enable focus trap within drawer
    trapHandler = (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        closeDrawer();
        return;
      }
      if (e.key !== "Tab") return;
      const focusable = drawer.querySelectorAll(
        'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const active = document.activeElement;
      if (e.shiftKey && active === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && active === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", trapHandler, true);
  }
  function closeDrawer() {
    drawer.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    backdrop.hidden = true;
    if (trapHandler) {
      document.removeEventListener("keydown", trapHandler, true);
      trapHandler = null;
    }
    if (restoreFocusEl && typeof restoreFocusEl.focus === "function") {
      restoreFocusEl.focus();
      restoreFocusEl = null;
    }
  }
  openSettings.addEventListener("click", openDrawer);
  closeSettings.addEventListener("click", closeDrawer);
  backdrop.addEventListener("click", closeDrawer);

  // Submit form with Enter key
  intentForm.addEventListener("submit", (e) => {
    e.preventDefault();
    runIntentBtn.click();
  });

  checkHealthBtn.addEventListener("click", async () => {
    healthOut.textContent = "Checking...";
    try {
      const res = await fetch(`/health`);
      const json = await res.json();
      healthOut.textContent = JSON.stringify(json, null, 2);
      healthOut.style.borderColor = "#22305a";
    } catch (e) {
      healthOut.textContent = `Error: ${e}`;
      healthOut.style.borderColor = "#ff6b6b";
    }
  });

  // Fetch and render OpenAPI schema for /api/intent
  async function loadSchema() {
    try {
      const res = await fetch(`/openapi.json`);
      const spec = await res.json();
      const path = spec.paths?.["/api/intent"]; // POST
      const post = path?.post;
      if (!post) {
        schemaOut.textContent = "No schema found for /api/intent";
        return;
      }
      const req = post.requestBody?.content?.["application/json"]?.schema || {};
      const beautified = JSON.stringify(req, null, 2);
      schemaOut.textContent = beautified;
    } catch (e) {
      schemaOut.textContent = `Error loading OpenAPI: ${e}`;
    }
  }
  loadSchema();

  // Examples
  for (const el of document.querySelectorAll(".example")) {
    el.addEventListener("click", () => {
      const txt = el.getAttribute("data-example") || "";
      promptEl.value = txt;
      promptEl.focus();
    });
  }

  function clearErrors() {
    for (const [input, label] of [
      [promptEl, promptErr],
      [projectIdEl, projectIdErr],
      [workspaceIdEl, workspaceIdErr],
    ]) {
      input.classList.remove("err");
      if (label) label.textContent = "";
    }
  }

  function validate() {
    clearErrors();
    let ok = true;
    if (!promptEl.value.trim()) {
      promptEl.classList.add("err");
      promptErr.textContent = "Prompt is required";
      ok = false;
    }
    // project/workspace optional: add any custom rules if needed
    return ok;
  }

  function buildCurl() {
    const origin = window.location.origin;
    const apiKey = (apiKeyEl.value || "").trim();
    const projectId = projectIdEl.value.trim();
    const workspaceId = workspaceIdEl.value.trim();
    const payload = {
      prompt: promptEl.value.trim(),
      ...(projectId ? { projectId } : {}),
      ...(workspaceId ? { workspaceId } : {}),
    };
    const parts = [
      `curl -s -X POST \\\n+  '${origin}/api/intent' \\\n+  -H 'Content-Type: application/json'`,
      apiKey ? `  -H 'X-API-Key: ${apiKey.replace(/'/g, "'\\''")}'` : undefined,
      `  -d '${JSON.stringify(payload).replace(/'/g, "'\\''")}'`,
    ].filter(Boolean);
    return parts.join("\n");
  }

  copyCurlBtn.addEventListener("click", async () => {
    const cmd = buildCurl();
    try {
      await navigator.clipboard.writeText(cmd);
      intentStatus.textContent = "cURL copied";
      setTimeout(() => (intentStatus.textContent = ""), 1200);
    } catch (e) {
      intentStatus.textContent = "Unable to copy cURL";
    }
  });

  runIntentBtn.addEventListener("click", async () => {
    clearErrors();
    if (!validate()) {
      intentStatus.textContent = "Fix validation errors";
      return;
    }
    const apiKey = apiKeyEl.value.trim();
    if (!apiKey) {
      intentStatus.textContent = "Enter API key in Settings";
      openDrawer();
      return;
    }
    const prompt = promptEl.value.trim();
    const projectId = projectIdEl.value.trim() || undefined;
    const workspaceId = workspaceIdEl.value.trim() || undefined;

    intentStatus.textContent = "Running...";
    planOut.textContent = logsOut.textContent = artifactsOut.textContent = rawOut.textContent = "";
    runIntentBtn.disabled = true;
    copyCurlBtn.disabled = true;
    try {
      const res = await fetch(`/api/intent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey,
        },
        body: JSON.stringify({ prompt, projectId, workspaceId }),
      });

      const text = await res.text();
      let json;
      try { json = JSON.parse(text); } catch (_) { json = { error: text }; }

      rawOut.textContent = JSON.stringify(json, null, 2);

      if (!res.ok) {
        intentStatus.textContent = `Error: ${res.status}`;
        return;
      }

      const plan = json.plan || [];
      planOut.textContent = plan.length ? JSON.stringify(plan, null, 2) : "No plan returned";
      const logs = json.logs || [];
      logsOut.textContent = logs.join("\n");
      const artifacts = json.artifacts || [];
      artifactsOut.textContent = JSON.stringify(artifacts, null, 2);
      intentStatus.textContent = "Done";
    } catch (e) {
      intentStatus.textContent = `Error: ${e}`;
    } finally {
      runIntentBtn.disabled = false;
      copyCurlBtn.disabled = false;
    }
  });
})();
