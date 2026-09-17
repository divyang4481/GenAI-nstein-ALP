// Dynamic API & WebSocket URLs based on current browser host (works on any machine / Docker / localhost)
const host = typeof window !== "undefined" && window.location.hostname ? window.location.hostname : "localhost";
const API_BASE = import.meta.env.VITE_API_BASE || `http://${host}:8000/api`;
const WS_BASE = import.meta.env.VITE_WS_BASE || `ws://${host}:8000/ws`;

const parseResponse = async (res) => {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API request failed (${res.status})`);
  }
  return res.json();
};

export const fetchOrders = async () => {
  const res = await fetch(`${API_BASE}/orders`);
  return parseResponse(res);
};

export const fetchIncidents = async () => {
  const res = await fetch(`${API_BASE}/incidents`);
  return parseResponse(res);
};

export const fetchIncidentDetails = async (incidentId) => {
  const res = await fetch(`${API_BASE}/incidents/${incidentId}`);
  return parseResponse(res);
};

export const submitDecision = async (incidentId, decision, reviewerNotes, reviewerName) => {
  const res = await fetch(`${API_BASE}/incidents/${incidentId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision,
      reviewer_notes: reviewerNotes,
      reviewer_name: reviewerName
    })
  });
  return parseResponse(res);
};

export const triggerInvestigation = async (orderId) => {
  const res = await fetch(`${API_BASE}/investigate/${orderId}`, {
    method: "POST"
  });
  return parseResponse(res);
};

export const fetchMetrics = async () => {
  const res = await fetch(`${API_BASE}/metrics`);
  return parseResponse(res);
};

export const fetchPolicies = async () => {
  const res = await fetch(`${API_BASE}/policies`);
  return parseResponse(res);
};

export const fetchAuditLedger = async () => {
  const res = await fetch(`${API_BASE}/audit-ledger`);
  return parseResponse(res);
};

export const runBenchmark = async () => {
  const res = await fetch(`${API_BASE}/eval/benchmark`);
  return parseResponse(res);
};

export const fetchMcpManifest = async () => {
  const res = await fetch(`${API_BASE}/mcp/manifest`);
  return parseResponse(res);
};

export const fetchLlmStatus = async () => {
  const res = await fetch(`${API_BASE}/llm/status`);
  return parseResponse(res);
};

export const askCase = async (orderId, question) => {
  const res = await fetch(`${API_BASE}/cases/${orderId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  return parseResponse(res);
};

// Replay Engine Controls
export const startReplay = async () => fetch(`${API_BASE}/replay/start`, { method: "POST" });
export const pauseReplay = async () => fetch(`${API_BASE}/replay/pause`, { method: "POST" });
export const resetReplay = async () => fetch(`${API_BASE}/replay/reset`, { method: "POST" });
export const triggerNextEvent = async () => fetch(`${API_BASE}/replay/next`, { method: "POST" });
export const setReplaySpeed = async (intervalSeconds) => {
  return fetch(`${API_BASE}/replay/speed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ interval_seconds: intervalSeconds })
  });
};

export const connectWebSocket = (onMessage, onOpen, onClose) => {
  let ws;
  let retryTimer;
  let stopped = false;

  const connect = () => {
    if (stopped) return;
    ws = new WebSocket(WS_BASE);

  ws.onopen = () => {
    console.log(`WebSocket connected to RetailFlow backend at ${WS_BASE}`);
    if (onOpen) onOpen();
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (err) {
      console.error("Failed to parse WS message", err);
    }
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected. Retrying in 3s...");
    if (onClose) onClose();
    if (!stopped) retryTimer = setTimeout(connect, 3000);
  };
  };
  connect();
  return {
    close() {
      stopped = true;
      clearTimeout(retryTimer);
      if (ws && ws.readyState < WebSocket.CLOSING) ws.close();
    }
  };
};
