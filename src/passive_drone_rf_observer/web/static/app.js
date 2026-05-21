const statusRunning = document.getElementById("status-running");
const statusEvents = document.getElementById("status-events");
const statusDroneLike = document.getElementById("status-drone-like");
const statusLastAlert = document.getElementById("status-last-alert");
const statusRisk = document.getElementById("status-risk");
const statusWifiEnabled = document.getElementById("status-wifi-enabled");
const statusWifiLast = document.getElementById("status-wifi-last");
const configThreshold = document.getElementById("config-threshold");
const configWindow = document.getElementById("config-window");
const configInterval = document.getElementById("config-interval");
const configLogPath = document.getElementById("config-log-path");
const eventsBody = document.getElementById("events-body");
const wifiBody = document.getElementById("wifi-body");
const wifiEnvironmentBody = document.getElementById("wifi-environment-body");
const alertsList = document.getElementById("alerts-list");
const startButton = document.getElementById("start-btn");
const stopButton = document.getElementById("stop-btn");
const clearButton = document.getElementById("clear-btn");
const wifiScanButton = document.getElementById("wifi-scan-btn");
const wifiClearButton = document.getElementById("wifi-clear-btn");
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

function renderWifiObservations(observations) {
  wifiBody.innerHTML = "";
  for (const obs of observations.slice(0, 20)) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${obs.timestamp_iso}</td>
      <td>${obs.ssid}</td>
      <td>${obs.bssid_hash.slice(0, 12)}</td>
      <td>${obs.signal_percent}</td>
      <td>${obs.channel ?? "-"}</td>
      <td>${obs.radio_type ?? "-"}</td>
      <td>${obs.authentication ?? "-"}</td>
    `;
    wifiBody.appendChild(row);
  }
}

function renderWifiEnvironmentEvents(events) {
  wifiEnvironmentBody.innerHTML = "";
  for (const event of events.slice(0, 20)) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${new Date(event.timestamp * 1000).toLocaleTimeString()}</td>
      <td>${event.event_type}</td>
      <td>${event.score.toFixed(2)}</td>
      <td>${event.explanation}</td>
      <td>${event.source}</td>
    `;
    wifiEnvironmentBody.appendChild(row);
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
  statusWifiEnabled.textContent = status.real_wifi_enabled ? "true" : "false";
  statusWifiLast.textContent = status.last_wifi_scan_ts ? new Date(status.last_wifi_scan_ts * 1000).toLocaleTimeString() : "none";
  modeSelect.value = status.mode;
}

async function refreshWifi() {
  const observations = await fetchJson("/api/wifi/observations");
  renderWifiObservations(observations);
}

async function refreshWifiEnvironmentEvents() {
  const events = await fetchJson("/api/wifi/environment-events");
  renderWifiEnvironmentEvents(events);
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
    await refreshWifi();
    await refreshWifiEnvironmentEvents();
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

wifiScanButton.addEventListener("click", async () => {
  await fetchJson("/api/wifi/scan", { method: "POST" });
  await refresh();
});

wifiClearButton.addEventListener("click", async () => {
  await fetchJson("/api/wifi/clear", { method: "POST" });
  await refresh();
});

refresh();
setInterval(refresh, 1000);
