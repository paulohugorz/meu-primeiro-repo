let protocol = null;
let session = null;
let stepIndex = 0;
const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {"Content-Type": "application/json"},
    ...options
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "Erro");
  return body;
}

async function fileToBase64(file) {
  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}

function renderStep() {
  const step = protocol.steps[stepIndex];
  $("progress").value = stepIndex + 1;
  $("progressText").textContent = `${stepIndex + 1}/${protocol.steps.length}`;
  $("stepContainer").innerHTML = `
    <article class="capture-card">
      <p class="eyebrow">Etapa ${step.sequence}</p>
      <h3>${step.title}</h3>
      <p>${step.instruction}</p>
      <label>Imagem
        <input id="captureFile" type="file"
          accept="image/jpeg,image/png,image/webp" capture="environment">
      </label>
      <div class="quality">
        <label><input id="focusOk" type="checkbox"> Foco adequado</label>
        <label><input id="lightingOk" type="checkbox"> Iluminação adequada</label>
        <label><input id="fillsFrame" type="checkbox"> Amostra ocupa o quadro</label>
        <label><input id="noLeak" type="checkbox"> Sem etiqueta ou nome revelador</label>
      </div>
      <p class="muted">Os controles começam desmarcados. A confirmação é registrada no nome do operador.</p>
      <button id="saveCapture">Salvar esta captura</button>
      <p id="stepStatus" class="status"></p>
    </article>`;
  $("saveCapture").onclick = saveCapture;
}

async function saveCapture() {
  const file = $("captureFile").files[0];
  if (!file) return $("stepStatus").textContent = "Selecione uma imagem.";
  const operator = $("operatorId").value.trim();
  if (!operator) return $("stepStatus").textContent = "Informe o operador.";
  $("stepStatus").textContent = "Validando assinatura, dimensões e decodificação…";
  const step = protocol.steps[stepIndex];
  try {
    const result = await api(`/api/sessions/${encodeURIComponent(session.session_id)}/captures`, {
      method: "POST",
      body: JSON.stringify({
        shot_type: step.shot_type,
        mime_type: file.type,
        file_name: file.name,
        data_base64: await fileToBase64(file),
        quality_confirmed_by_actor_id: operator,
        quality: {
          focus_ok: $("focusOk").checked,
          lighting_ok: $("lightingOk").checked,
          sample_fills_frame: $("fillsFrame").checked,
          no_label_leak: $("noLeak").checked
        }
      })
    });
    $("stepStatus").textContent = result.accepted
      ? `Aceita · ${result.width_px}×${result.height_px} · Evidence ${result.evidence.evidence_id}`
      : `Rejeitada · ${result.rejection_reasons.join(", ")}`;
  } catch (error) {
    $("stepStatus").textContent = error.message;
  }
}

async function start() {
  protocol = await api("/api/protocol");
  session = await api("/api/sessions", {
    method: "POST",
    body: JSON.stringify({
      sample_ref: $("sampleId").value,
      operator_id: $("operatorId").value,
      device_id: navigator.userAgent
    })
  });
  $("capturePanel").classList.remove("hidden");
  stepIndex = 0;
  renderStep();
}

async function finalize() {
  const result = await api(`/api/sessions/${encodeURIComponent(session.session_id)}/finalize`, {
    method: "POST", body: "{}"
  });
  $("captureResult").textContent = JSON.stringify({
    status: result.status,
    ops_id: result.ops_id,
    service_sample_id: result.service_sample_id,
    textile_sample_node_id: result.textile_sample_node_id,
    ready_for_baseline: result.ready_for_baseline,
    missing_shot_types: result.completion.missing_shot_types
  }, null, 2);
}

async function refreshTasks() {
  const tasks = await api("/api/tasks");
  $("tasks").innerHTML = tasks.length ? tasks.map(t => `
    <article class="task">
      <strong>${escapeHtml(t.task_type)}</strong>
      <div class="muted">${escapeHtml(t.sample_id)} · ${escapeHtml(t.priority)} · ${escapeHtml(t.status)}</div>
      <div class="status">mode=${escapeHtml(t.mode)} affects_official_decision=${escapeHtml(t.affects_official_decision)}</div>
    </article>`).join("") : `<p class="muted">Nenhuma tarefa.</p>`;
}

$("startButton").onclick = start;
$("previousButton").onclick = () => { stepIndex = Math.max(0, stepIndex - 1); renderStep(); };
$("nextButton").onclick = () => { stepIndex = Math.min(protocol.steps.length - 1, stepIndex + 1); renderStep(); };
$("finalizeButton").onclick = finalize;
$("refreshTasks").onclick = refreshTasks;
refreshTasks();
