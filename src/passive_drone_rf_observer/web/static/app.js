const statusRunning = document.getElementById("status-running");
const statusEvents = document.getElementById("status-events");
const statusDroneLike = document.getElementById("status-drone-like");
const statusLastAlert = document.getElementById("status-last-alert");
const statusRisk = document.getElementById("status-risk");
const configThreshold = document.getElementById("config-threshold");
const configWindow = document.getElementById("config-window");
const configInterval = document.getElementById("config-interval");
const configLogPath = document.getElementById("config-log-path");
const eventsBody = document.getElementById("events-body");
const alertsList = document.getElementById("alerts-list");
const startButton = document.getElementById("start-btn");
const stopButton = document.getElementById("stop-btn");
const clearButton = document.getElementById("clear-btn");
const modeSelect = document.getElementById("mode-select");

async function fetchJson(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} ${response.statusText}`);
  }
  return response.json();
}

function renderEvents(events) {
  eventsBody.innerHTML = "";
  for (const event of events.slice(0, 20)) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${event.timestamp_iso}</td>
      <td>${event.frequency_mhz.toFixed(3)}</td>
      <td>${event.rssi_dbm.toFixed(1)}</td>
      <td>${event.duration_ms.toFixed(1)}</td>
      <td>${event.label}</td>
      <td>${event.score.toFixed(2)}</td>
      <td>${event.explanation}</td>
    `;
    eventsBody.appendChild(row);
  }
}

function renderAlerts(alerts) {
  alertsList.innerHTML = "";
  for (const alert of alerts.slice(0, 10)) {
    const card = document.createElement("div");
    card.className = `alert-card alert-${alert.level}`;
    card.innerHTML = `<strong>${alert.level.toUpperCase()}</strong> - ${alert.message} <span>${new Date(alert.timestamp * 1000).toLocaleTimeString()}</span>`;
    alertsList.appendChild(card);
  }
}

async function refreshStatus() {
  const status = await fetchJson("/api/status");
  statusRunning.textContent = status.running ? "running" : "stopped";
  statusEvents.textContent = status.num_events_received;
  statusDroneLike.textContent = status.num_drone_like;
  statusLastAlert.textContent = status.last_alert ? `${status.last_alert.level} (${status.last_alert.probability.toFixed(2)})` : "none";
  statusRisk.textContent = status.risk_level;
  configThreshold.textContent = status.config.detection_threshold;
  configWindow.textContent = `${status.config.correlation_window_s}s`;
  configInterval.textContent = `${status.config.event_interval_s}s`;
  configLogPath.textContent = status.config.log_db_path;
  modeSelect.value = status.mode;
}

async function refreshEvents() {
  const events = await fetchJson("/api/events");
  renderEvents(events);
}

async function refreshAlerts() {
  const alerts = await fetchJson("/api/alerts");
  renderAlerts(alerts);
}

async function refresh() {
  try {
    await refreshStatus();
    await refreshEvents();
    await refreshAlerts();
  } catch (error) {
    console.error(error);
  }
}

startButton.addEventListener("click", async () => {
  await fetchJson("/api/simulation/start", { method: "POST" });
  await refresh();
});

stopButton.addEventListener("click", async () => {
  await fetchJson("/api/simulation/stop", { method: "POST" });
  await refresh();
});

clearButton.addEventListener("click", async () => {
  await fetchJson("/api/events/clear", { method: "POST" });
  await refresh();
});

modeSelect.addEventListener("change", async () => {
  await fetchJson("/api/simulation/mode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: modeSelect.value }),
  });
  await refresh();
});

refresh();
setInterval(refresh, 1000);
