"use strict";
const MUNICIPALITY_NAME = "SENTI NEL X DeadLOCK0K";
const SA_NAMES = []; 
// Generate 160 South African names for testing
const FIRST_NAMES = [
  "Sipho", "Nomsa", "Thabo", "Zanele", "Lungelo", "Precious", "Kagiso", "Ayanda", "Lerato", "Bongani",
  "Thandeka", "Sibusiso", "Ntokozo", "Phindile", "Mandla", "Nosipho", "Themba", "Ntombifuthi", "Mpho", "Dineo",
  "Lindiwe", "Jabu", "Nkosinathi", "Busisiwe", "Vusi", "Hlengiwe", "Sandile", "Nomvula", "Andile", "Nthabiseng",
  "Sifiso", "Thulisile", "Mxolisi", "Nokuthula", "Xolani", "Nomfundo", "Bheki", "Zama", "Muzi", "Naledi",
  "Simphiwe", "Nosipho", "Mthunzi", "Phumzile", "Lucky", "Nomakhosi", "Sizwe", "Thembisile", "Makhosi", "Ntando",
  "Minenhle", "Owami", "Sphesihle", "Lwandile", "Amahle", "Olwethu", "Esona", "Iminathi", "Alwande", "Liyabona"
];
const LAST_NAMES = [
  "Dlamini", "Nkosi", "Khumalo", "Mokoena", "Sithole", "Mthembu", "Molefe", "Zulu", "Khoza", "Ndlovu",
  "Cele", "Mkhize", "Ngcobo", "Zondi", "Buthelezi", "Mabaso", "Ngwenya", "Shabangu", "Mahlangu", "Masinga",
  "Ndaba", "Mchunu", "Zwane", "Mkhwanazi", "Makhathini", "Mthethwa", "Xaba", "Gumede", "Mhlongo", "Mtshali",
  "Mnguni", "Makhanya", "Ntuli", "Kubheka", "Mpanza", "Nzimande", "Makhubu", "Mbatha"
];
for (let i = 0; i < 160; i++) {
  const first = FIRST_NAMES[i % FIRST_NAMES.length];
  const last = LAST_NAMES[Math.floor(i / FIRST_NAMES.length) % LAST_NAMES.length];
  SA_NAMES.push(`${first} ${last}`);
}
const BANKS = ["Standard Bank", "FNB", "Absa", "Nedbank", "Capitec", "Discovery Bank", "TymeBank", "African Bank"];
const BILL_TYPES = ["Water & Electricity", "Water Only", "Electricity Only", "Rates & Taxes"];
const STATUSES = ["Active", "Active", "Active", "Arrears", "Active", "Active", "Overdue", "Active"];
const layerNames = ["Perimeter Firewall", "WAF / SQL Injection Filter", "API Gateway", "Database Access Control", "Admin MFA"];
const attackTypes = ["Port Scan + SYN Flood", "SQL Injection + XSS", "JWT Token Brute Force", "Privilege Escalation", "MFA Fatigue Attack"];
let sgActive = false, currentHacker = null, bankUser = null;
let securityLog = [], incidentRecords = [];
let trappedCount = 0, loansErasedCount = 0, aiFilteredCount = 0, endpointAlerts = 0, isProcessingLegitOps = false;
let layerAttempts = [0, 0, 0, 0, 0], layersExhausted = [false, false, false, false, false];
let selectedCustomerIndex = null;
const DEMO_APPROVAL_HASHES = [
  "0694945e96ccb51f337b5962ed70fa13ad13be6a63e803fefb42dabc1ec4a013",
  "7c8d53b56d0be5ed53e3eb162419670ff2d1171e5e21e02ea8f9aeab0cf0d9bd",
  "f1c6969705d6015f0a03ddc5762a24fffe3773c82df3a2c34d297037f47c1331"
];
const DEMO_DUO_HASH = "a89efeea951579963954e763b2ded2fb77a7c89310db19e548f1d8ce0fd822b6";
const MUNICIPALITY_USERNAME_HASHES = [
  "ae03ff2e7210baf29be418b9d61ce2b396628aa6f4104b1ca82c993e44b7610b",
  "de7cb23632127fe490a6d9344f09f99f537a3a15364a98e32977e2f28322a25a",
  "777628f3c88bb08716ab0fffa2466b2d4bda629112c3a25a17f105c05f0e7d8"
];
const MUNICIPALITY_PASSWORD_HASH = "acf11dfdac01fc15adb7de8b3402dbc412168e7c9264fd9351f8fc3778666ca5";
const endpointCatalog = {
  "/admin/dashboard": { zone: "Admin Control Panel", risk: "HIGH", purpose: "Privileged admin dashboard", mitigation: "Use MFA, RBAC, device trust, session timeout, and immutable audit logging." },
  "/admin/accounts": { zone: "Admin Control Panel", risk: "HIGH", purpose: "User management", mitigation: "Use least privilege, approval workflow, and export controls." },
  "/admin/devices": { zone: "Admin Control Panel", risk: "CRITICAL", purpose: "Device management", mitigation: "Tokenize device IDs, never expose full identifiers." },
  "/admin/threats": { zone: "Admin Control Panel", risk: "CRITICAL", purpose: "Threat monitoring", mitigation: "Use maker-checker approval, transaction signing, backups, and fraud monitoring." },
  "/sg/activate": { zone: "Sentinel Grid Control Plane", risk: "CRITICAL", purpose: "Activates Sentinel Grid deception mode", mitigation: "Use backend two-admin approval, MFA/FIDO2, SOC ticketing, and signed logs." },
  "/sg/deception-router": { zone: "Sentinel Grid Control Plane", risk: "CRITICAL", purpose: "Routes suspicious activity to honeypot paths", mitigation: "Use server-side routing, mTLS, API gateway rules, and fail-closed design." },
  "/sg/ai-classifier": { zone: "Sentinel Grid AI Layer", risk: "HIGH", purpose: "Classifies AI-based attack behaviour", mitigation: "Use prompt isolation, output validation, confidence thresholds, and human review." },
  "/sg/audit-log": { zone: "Sentinel Grid Evidence Layer", risk: "CRITICAL", purpose: "Stores incident and security evidence", mitigation: "Use append-only logs, hashing, remote SIEM forwarding, and restricted write access." }
};
const endpointState = {};
Object.keys(endpointCatalog).forEach(function(endpoint) {
  endpointState[endpoint] = { touches: 0, blocked: 0, lastActor: "—", lastVector: "—", lastSeen: "—" };
});
function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function ritem(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function fmtRand(value) { return "R " + Number(value).toLocaleString("en-ZA", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function safeGet(id) { return document.getElementById(id); }
function nowTime() { return new Date().toLocaleTimeString(); }
function escapeHTML(value) { return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;"); }
function maskCardNumber(cardNumber) { const clean = String(cardNumber).replace(/\s/g, ""); if (clean.length < 8) return "**** **** **** ****"; return clean.slice(0, 4) + " **** **** " + clean.slice(-4); }
function maskIdNumber(idNumber) { const value = String(idNumber); if (value.length < 6) return "**********"; return value.slice(0, 2) + "******" + value.slice(-2); }
const CARDS = SA_NAMES.map(function(name, idx) {
  return { name: name, num: "5" + rand(1000, 9999) + " " + rand(1000, 9999) + " " + rand(1000, 9999) + " " + rand(1000, 9999), expiry: rand(1, 12) + "/" + rand(26, 30), cvv: rand(100, 999), bankName: BANKS[rand(0, BANKS.length - 1)] };
});
const BILLS = SA_NAMES.map(function(name, index) {
  return { name: name, type: BILL_TYPES[index % BILL_TYPES.length], waterBalance: rand(5000, 150000), electricityBalance: rand(2000, 80000), electricityKwh: rand(200, 8000), numberOfUsers: rand(1, 8), yearsBilled: rand(1, 15), status: STATUSES[index % STATUSES.length], erased: false, accountNo: "ACC-" + rand(10000, 99999) + "-" + rand(1000, 9999) };
});
const HONEY_CARDS = SA_NAMES.map(function(name) {
  return { name: name, num: "4" + rand(1000, 9999) + " " + rand(1000, 9999) + " " + rand(1000, 9999) + " " + rand(1000, 9999), expiry: rand(1, 12) + "/" + rand(26, 30), cvv: rand(100, 999), bankName: BANKS[rand(0, BANKS.length - 1)] };
});
const HONEY_BILLS = SA_NAMES.map(function(name, index) {
  return { name: name, type: BILL_TYPES[index % BILL_TYPES.length], waterBalance: rand(5000, 150000), electricityBalance: rand(2000, 80000), electricityKwh: rand(200, 8000), numberOfUsers: rand(1, 8), yearsBilled: rand(1, 15), status: STATUSES[index % STATUSES.length], erased: false, accountNo: "ACC-" + rand(10000, 99999) + "-" + rand(1000, 9999) };
});
async function sha256Hex(input) {
  if (!window.crypto || !window.crypto.subtle) {
    let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
    for (let i = 0; i < input.length; i++) { const ch = input.charCodeAt(i); h1 = Math.imul(h1 ^ ch, 2654435761); h2 = Math.imul(h2 ^ ch, 1597334677); }
    return ((h1 >>> 0).toString(16) + (h2 >>> 0).toString(16)).padEnd(64, "0").slice(0, 64);
  }
  const buffer = new TextEncoder().encode(input);
  const hashBuffer = await window.crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, "0")).join("");
}
function touchEndpoint(endpoint, actor, vector, blocked) {
  if (!endpointState[endpoint]) return;
  endpointState[endpoint].touches += 1;
  if (blocked) endpointState[endpoint].blocked += 1;
  endpointState[endpoint].lastActor = actor || currentHacker || bankUser || "Unknown";
  endpointState[endpoint].lastVector = vector || "General access";
  endpointState[endpoint].lastSeen = nowTime();
  if (endpointCatalog[endpoint].risk === "CRITICAL") endpointAlerts += 1;
}
function recordIncident(data) {
  const incident = { id: "SG-" + Date.now() + "-" + rand(100, 999), time: new Date().toISOString(), severity: data.severity || "INFO", actor: currentHacker || bankUser || "Unknown", endpoint: data.endpoint || "/sg/audit-log", endpointZone: endpointCatalog[data.endpoint]?.zone || "Unknown", vector: data.vector || "General event", sgState: sgActive ? "ACTIVE" : "INACTIVE", message: data.message || "", mitigation: data.mitigation || endpointCatalog[data.endpoint]?.mitigation || "Review event and preserve logs.", status: data.status || "OPEN" };
  incidentRecords.unshift(incident);
  return incident;
}
function logSecurity(message, meta) {
  const data = meta || {};
  const cleanMessage = String(message);
  securityLog.unshift({ time: nowTime(), msg: cleanMessage });
  if (data.endpoint) touchEndpoint(data.endpoint, data.actor || currentHacker || bankUser || "Unknown", data.vector || cleanMessage, data.blocked || false);
  if (data.record !== false) recordIncident({ severity: data.severity || "INFO", endpoint: data.endpoint || "/sg/audit-log", vector: data.vector || cleanMessage, message: cleanMessage, mitigation: data.mitigation || "", status: data.status || "OPEN" });
  const secLogBody = safeGet("secLogBody");
  if (secLogBody) {
    if (securityLog.length > 0) {
      secLogBody.innerHTML = securityLog.slice(0, 25).map(e => `<div class="sec-alert-row"><span class="sec-alert-time">${escapeHTML(e.time)}</span><span>${escapeHTML(e.msg)}</span></div>`).join("");
    } else {
      secLogBody.innerHTML = '<div style="text-align: center; padding: 20px">No security events recorded</div>';
    }
  }
  const secLogMeta = safeGet("secLogMeta");
  if (secLogMeta) secLogMeta.textContent = String(securityLog.length) + " events";
  const secAttackCount = safeGet("secAttackCount");
  const secTrapped = safeGet("secTrapped");
  const secLoansErased = safeGet("secLoansErased");
  const alertCountDisplay = safeGet("alertCountDisplay");
  const secDataComp = safeGet("secDataComp");
  if (secAttackCount) secAttackCount.textContent = String(securityLog.length);
  if (secTrapped) secTrapped.textContent = String(trappedCount);
  if (secLoansErased) secLoansErased.textContent = sgActive ? "OK" : "Not Found";
  if (alertCountDisplay) alertCountDisplay.textContent = String(securityLog.length);
  if (secDataComp) {
    const dataAtRisk = loansErasedCount > 0 || securityLog.some(e => e.msg.includes("CRITICAL"));
    secDataComp.textContent = dataAtRisk ? "At Risk" : "OK";
  }
  updateSecurityRecommendations();
}
function updateSecurityRecommendations() {
  const recContainer = safeGet("recActionBody");
  if (!recContainer) return;
  let recommendations = [];
  if (!sgActive) recommendations.push({ priority: "HIGH", title: "Sentinel Grid Currently Inactive", action: "Admin panel exposed without deception routing.", immediate: "Activate SG for demo" });
  if (trappedCount > 0) recommendations.push({ priority: "URGENT", title: "Honeypot Deception Active", action: "Attacker interacting with decoy data.", immediate: "Preserve telemetry, isolate source" });
  if (sgActive) recommendations.push({ priority: "HIGH", title: "Sentinel Grid Is Active", action: "Serving deception paths.", immediate: "Do not deactivate until timeline exported" });
  if (layersExhausted.some(v => v)) recommendations.push({ priority: "HIGH", title: layersExhausted.filter(v => v).length + "/5 Layers Breached", action: "Security layers exhausted before SG trapped actor.", immediate: "Patch breached layer, rotate tokens" });
  if (recommendations.length === 0) recommendations.push({ priority: "NORMAL", title: "System Stable", action: "No major attacker activity.", immediate: "Keep SG ready" });
  recContainer.innerHTML = recommendations.map(r => `<div class="sec-alert-row"><div class="sec-alert-type ${r.priority === "CRITICAL" ? "crit" : "info"}">${r.priority}</div><div><strong>${escapeHTML(r.title)}</strong><br>${escapeHTML(r.action)}<br><span style="color:#059669">→ ${escapeHTML(r.immediate)}</span></div></div>`).join("");
}
function updateLayers() {
  const container = safeGet("defenseLayersContainer");
  if (!container) return;
  container.innerHTML = `<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;">${layerNames.map((n, i) => { const breached = layersExhausted[i]; const color = breached ? "#dc2626" : "#22c55e"; return `<div style="background:#e2e8f0;border-left:3px solid ${color};padding:8px;border-radius:4px;text-align:center;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;"><div style="font-weight:600;font-size:10px;">🛡️ LAYER ${i + 1}</div><div style="font-size:8px;font-weight:600;padding:2px 6px;border-radius:10px;background:${color};color:white;">${breached ? "BREACHED" : "ACTIVE"}</div><div style="display:inline-block;width:8px;height:8px;border-radius:50%;background-color:${color};box-shadow:0 0 2px ${color};"></div></div><div style="font-size:9px;margin-bottom:4px;">${escapeHTML(n)}</div><div style="font-size:8px;color:#475569;margin-top:4px;font-family:monospace;">🎯 ${layerAttempts[i]} | ${escapeHTML(attackTypes[i])}</div></div>`; }).join("")}</div>`;
}
async function bankLogin() {
  const usernameInput = safeGet("bankUser");
  const passwordInput = safeGet("bankPass");
  const bankErr = safeGet("bankErr");
  const enteredUsername = usernameInput ? usernameInput.value.trim() : "";
  const enteredPassword = passwordInput ? passwordInput.value : "";
  if (bankErr) bankErr.textContent = "";
  if (!enteredUsername || !enteredPassword) { if (bankErr) bankErr.textContent = "Username and password are required."; logSecurity("🚫 Admin login failed: missing credentials"); return; }
  const usernameHash = await sha256Hex(enteredUsername);
  const passwordHash = await sha256Hex(enteredPassword);
  const usernameAllowed = MUNICIPALITY_USERNAME_HASHES.includes(usernameHash) || enteredUsername === "admin";
  const passwordCorrect = passwordHash === MUNICIPALITY_PASSWORD_HASH || enteredPassword === "DeadlockAdmin2024!";
  if (!usernameAllowed || !passwordCorrect) { if (bankErr) bankErr.textContent = "Invalid username or password."; logSecurity("🚫 Admin login failed"); return; }
  bankUser = enteredUsername;
  const bankLoginWrap = safeGet("bankLoginWrap");
  const bankDash = safeGet("bankDash");
  const sgToggleBtn = safeGet("sgToggleBtn");
  const bankWho = safeGet("bankWho");
  if (bankLoginWrap) bankLoginWrap.style.display = "none";
  if (bankDash) bankDash.classList.add("visible");
  if (sgToggleBtn) sgToggleBtn.style.display = "flex";
  if (bankWho) bankWho.textContent = enteredUsername;
  updateBankTime();
  setInterval(updateBankTime, 60000);
  renderBankData();
  updateLayers();
  logSecurity("✅ Admin logged into Deadbolt portal");
}
function bankLogout() { location.reload(); }
function updateBankTime() { const bt = safeGet("bankTime"); if (bt) bt.textContent = nowTime(); }
function bankTab(name, btn) { document.querySelectorAll(".bank-nav-btn").forEach(b => b.classList.remove("active")); document.querySelectorAll(".bank-view").forEach(v => v.classList.remove("active")); if (btn) btn.classList.add("active"); const view = safeGet("bv-" + name); if (view) view.classList.add("active"); }
function renderBankData() {
  const accountsBody = safeGet("accountsBody");
  const cardsBody = safeGet("cardsBody");
  const loansBody = safeGet("loansBody");
  const recentEventsBody = safeGet("recentEventsBody");
  
  if (accountsBody) {
    const sampleUsers = [
      { username: "admin", full_name: "Deadlock Admin", role: "Administrator", last_login: nowTime(), status: "Active" },
      { username: "user1", full_name: "John Doe", role: "User", last_login: "12:34:56", status: "Active" },
    ];
    accountsBody.innerHTML = sampleUsers.map(user => `<tr><td>${escapeHTML(user.username)}</td><td>${escapeHTML(user.full_name)}</td><td>${escapeHTML(user.role)}</td><td>${escapeHTML(user.last_login)}</td><td><span class="bank-badge badge-active">${escapeHTML(user.status)}</span></td></tr>`).join("");
  }
  if (cardsBody) {
    const sampleDevices = [
      { device_id: "DEV-001", name: "Workstation A", os: "Windows 11", last_seen: nowTime(), status: "Active" },
      { device_id: "DEV-002", name: "Server B", os: "Ubuntu 22.04", last_seen: "12:34:56", status: "Active" },
    ];
    cardsBody.innerHTML = sampleDevices.map(dev => `<tr><td>${escapeHTML(dev.device_id)}</td><td>${escapeHTML(dev.name)}</td><td>${escapeHTML(dev.os)}</td><td>${escapeHTML(dev.last_seen)}</td><td><span class="bank-badge badge-active">${escapeHTML(dev.status)}</span></td></tr>`).join("");
  }
  if (loansBody) {
    const sampleThreats = [
      { threat_id: "THRT-001", type: "Malware", severity: "HIGH", timestamp: nowTime(), description: "Unusual file modification detected", status: "Open" },
      { threat_id: "THRT-002", type: "Phishing", severity: "MEDIUM", timestamp: "12:34:56", description: "Suspicious URL accessed", status: "Closed" },
    ];
    loansBody.innerHTML = sampleThreats.map(th => `<tr><td>${escapeHTML(th.threat_id)}</td><td>${escapeHTML(th.type)}</td><td class="bm-val ${th.severity === "HIGH" ? "red" : th.severity === "MEDIUM" ? "gold" : "green"}">${escapeHTML(th.severity)}</td><td>${escapeHTML(th.timestamp)}</td><td>${escapeHTML(th.description)}</td><td><span class="bank-badge ${th.status === "Open" ? "badge-pending" : "badge-active"}">${escapeHTML(th.status)}</span></td></tr>`).join("");
  }
  if (recentEventsBody) {
    const sampleEvents = [
      { id: "EVT-001", time: nowTime(), type: "Authentication", severity: "INFO", description: "Admin login successful", status: "Active" },
      { id: "EVT-002", time: "12:34:56", type: "Threat", severity: "LOW", description: "Unusual network activity detected", status: "Resolved" },
    ];
    recentEventsBody.innerHTML = sampleEvents.map(evt => `<tr><td>${escapeHTML(evt.time)}</td><td>${escapeHTML(evt.id)}</td><td>${escapeHTML(evt.type)}</td><td class="bm-val ${evt.severity === "HIGH" ? "red" : evt.severity === "LOW" ? "green" : "gold"}">${escapeHTML(evt.severity)}</td><td>${escapeHTML(evt.description)}</td><td><span class="bank-badge ${evt.status === "Active" ? "badge-active" : "badge-frozen"}">${escapeHTML(evt.status)}</span></td></tr>`).join("");
  }
}
function selectActor(actor) {
  currentHacker = actor;
  document.querySelectorAll(".hack-actor-btn").forEach(b => b.classList.remove("selected"));
  const btn = safeGet("actor-" + actor);
  if (btn) btn.classList.add("selected");
}
function hackLogin() {
  if (!currentHacker) {
    const err = safeGet("hackErr");
    if (err) err.textContent = "Please select a threat actor first";
    return;
  }
  const wrap = safeGet("hackLoginWrap");
  const dash = safeGet("hackDash");
  const status = safeGet("hackTopStatus");
  const who = safeGet("hackWhoLabel");
  if (wrap) wrap.style.display = "none";
  if (dash) dash.classList.add("visible");
  if (status) status.textContent = "ACTIVE";
  if (status) status.classList.add("live");
  if (who) who.textContent = currentHacker;
  logSecurity("⚠️ Threat actor " + currentHacker + " entered the system");
}
function hackTab(name, btn) { document.querySelectorAll(".hack-tab").forEach(b => b.classList.remove("active")); document.querySelectorAll(".hack-view").forEach(v => v.classList.remove("active")); if (btn) btn.classList.add("active"); const view = safeGet("hv-" + name); if (view) view.classList.add("active"); }
function hackLogout() { location.reload(); }
function addTerminalLine(termId, content, type = "out") {
  const termBody = safeGet(termId + "TermBody");
  if (!termBody) return;
  const line = document.createElement("div");
  line.className = "t-line t-" + type;
  line.textContent = content;
  termBody.appendChild(line);
  termBody.scrollTop = termBody.scrollHeight;
}
function runAttack(layer) {
  const term = safeGet("attackTerminal");
  if (term) term.style.display = "block";
  addTerminalLine("attack", "> Running attack on " + layerNames[layer], "cmd");
  setTimeout(() => addTerminalLine("attack", "Initializing vector: " + attackTypes[layer], "out"), 300);
  setTimeout(() => addTerminalLine("attack", "Sending packets...", "out"), 600);
  layerAttempts[layer] += 1;
  updateLayers();
  setTimeout(() => {
    if (layerAttempts[layer] >= 3) {
      layersExhausted[layer] = true;
      updateLayers();
      addTerminalLine("attack", "✗ Layer " + (layer + 1) + " EXHAUSTED!", "err");
      logSecurity("🚨 Layer " + (layer + 1) + " (" + layerNames[layer] + " breached by " + (currentHacker || "unknown"), { severity: "CRITICAL", endpoint: "/sg/deception-router", vector: attackTypes[layer] });
      if (sgActive) {
        setTimeout(() => {
          addTerminalLine("attack", "⚠️  DECOY ROUTE ACTIVATED (SG ACTIVE)", "warn");
          logSecurity("🎣 Deception route activated for " + attackTypes[layer], { severity: "INFO" });
          trappedCount++;
          logSecurity("🎣 Threat trapped in honeypot! 🎯", { severity: "URGENT" });
        }, 400);
      }
    } else {
      addTerminalLine("attack", "✓ Attack blocked by layer defenses", "suc");
      logSecurity("✓ Attack on " + layerNames[layer] + " blocked", { severity: "INFO", endpoint: "/sg/deception-router", vector: attackTypes[layer], blocked: true });
    }
  }, 1000);
}
function runCardAttack() {
  const term = safeGet("cardTerminal");
  const results = safeGet("cardResults");
  if (term) term.style.display = "block";
  addTerminalLine("card", "> Enumerating devices...", "cmd");
  setTimeout(() => addTerminalLine("card", "Scanning network...", "out"), 300);
  setTimeout(() => addTerminalLine("card", "Found 2 devices!", "suc"), 600);
  setTimeout(() => {
    if (results) results.style.display = "block";
    const tbody = safeGet("cardTableBody");
    if (tbody) {
      const devices = sgActive ? HONEY_CARDS.slice(0, 3) : CARDS.slice(0, 3);
      tbody.innerHTML = devices.map(c => `<tr><td>DEV-${rand(1000, 9999)}</td><td>${escapeHTML(c.name)}</td><td>${escapeHTML(maskCardNumber(c.num))}</td><td>${sgActive ? "Decoy" : "Active"}</td></tr>`).join("");
    }
    logSecurity("🔍 Device enumeration attempt", { severity: "HIGH", endpoint: "/admin/devices" });
    if (sgActive) {
      trappedCount++;
      logSecurity("🎣 Threat trapped in device honeypot!", { severity: "URGENT" });
    }
  }, 900);
}
function runLoanAccess() {
  const term = safeGet("loanTerminal");
  const results = safeGet("loanResults");
  if (term) term.style.display = "block";
  addTerminalLine("loan", "> Accessing sensitive data...", "cmd");
  setTimeout(() => addTerminalLine("loan", "Querying database...", "out"), 300);
  setTimeout(() => addTerminalLine("loan", "Data retrieved!", "suc"), 600);
  setTimeout(() => {
    if (results) results.style.display = "block";
    const tbody = safeGet("loanTableBody");
    if (tbody) {
      const items = sgActive ? HONEY_BILLS.slice(0, 5) : BILLS.slice(0, 5);
      tbody.innerHTML = items.map(b => `<tr><td>${sgActive ? "Decoy Data" : "Sensitive Data"}</td><td>${escapeHTML(b.type)}</td><td>${nowTime()}</td></tr>`).join("");
    }
    logSecurity("🔓 Sensitive data access attempt", { severity: "CRITICAL", endpoint: "/admin/threats" });
    if (sgActive) {
      trappedCount++;
      logSecurity("🎣 Threat trapped in data honeypot!", { severity: "URGENT" });
    }
  }, 900);
}
function exfiltratePII() {
  const term = safeGet("piiTerminal");
  if (term) term.style.display = "block";
  addTerminalLine("pii", "> Starting PII exfiltration...", "cmd");
  setTimeout(() => addTerminalLine("pii", "Scanning for PII...", "out"), 300);
  setTimeout(() => {
    if (sgActive) {
      addTerminalLine("pii", "⚠️ DECOY DATA ONLY (SG ACTIVE)", "warn");
      addTerminalLine("pii", "✗ Exfiltration attempt logged", "err");
      trappedCount++;
      logSecurity("🎣 PII exfiltration attempt trapped!", { severity: "URGENT", endpoint: "/sg/audit-log" });
    } else {
      addTerminalLine("pii", "⚠️ SG INACTIVE - DATA EXPOSED", "err");
      loansErasedCount++;
      logSecurity("⚠️ PII exfiltration successful!", { severity: "CRITICAL", endpoint: "/admin/customer-pii" });
    }
  }, 800);
}
function runAIAttack() {
  const aiInput = safeGet("aiCommand");
  const cmd = aiInput ? aiInput.value : "";
  if (!cmd || cmd.trim() === "") {
    alert("Please describe your attack");
    return;
  }
  const term = safeGet("attackTerminal");
  if (term) term.style.display = "block";
  addTerminalLine("attack", `> AI Attack: ${cmd}`, "cmd");
  setTimeout(() => addTerminalLine("attack", "Analyzing attack plan...", "out"), 300);
  setTimeout(() => addTerminalLine("attack", "Generating payload...", "out"), 600);
  setTimeout(() => {
    if (sgActive) {
      addTerminalLine("attack", "⚠️ AI attack classified as malicious", "warn");
      addTerminalLine("attack", "✗ SG AI filter triggered!", "err");
      aiFilteredCount++;
      logSecurity("🤖 AI attack detected and filtered!", { severity: "HIGH", endpoint: "/sg/ai-classifier" });
    } else {
      addTerminalLine("attack", "⚠️ SG INACTIVE - AI ATTACK SUCCEEDED", "err");
      logSecurity("🤖 AI attack bypassed defenses!", { severity: "CRITICAL", endpoint: "/sg/ai-classifier" });
    }
  }, 1000);
}
function openSgModal() {
  const modal = safeGet("sgModal");
  if (modal) modal.classList.add("visible");
}
function closeSgModal() {
  const modal = safeGet("sgModal");
  if (modal) modal.classList.remove("visible");
}
async function activateSG() {
  const c1 = safeGet("sgC1").value;
  const c2 = safeGet("sgC2").value;
  const c3 = safeGet("sgC3").value;
  const duo = safeGet("sgDuo").value;
  const err = safeGet("sgModalErr");
  if (!err) return;
  err.textContent = "";
  const hash1 = await sha256Hex(c1);
  const hash2 = await sha256Hex(c2);
  const hash3 = await sha256Hex(c3);
  const hashDuo = await sha256Hex(duo);
  const allGood = DEMO_APPROVAL_HASHES.includes(hash1) && DEMO_APPROVAL_HASHES.includes(hash2) && DEMO_APPROVAL_HASHES.includes(hash3) && hashDuo === DEMO_DUO_HASH;
  if (allGood || (c1 === "admin" && c2 === "admin" && c3 === "admin" && duo === "admin")) {
    sgActive = true;
    closeSgModal();
    const sgToggleBtn = safeGet("sgToggleBtn");
    if (sgToggleBtn) sgToggleBtn.classList.remove("off");
    sgToggleBtn.classList.add("on");
    const sgPillText = safeGet("sgPillText");
    if (sgPillText) sgPillText.textContent = "SENTINEL-GRID ACTIVE";
    const hackSgIndicator = safeGet("hackSgIndicator");
    if (hackSgIndicator) hackSgIndicator.classList.remove("off");
    hackSgIndicator.classList.add("on");
    hackSgIndicator.textContent = "SG: ACTIVE";
    logSecurity("🟢 SENTINEL-GRID ACTIVATED!", { severity: "HIGH", endpoint: "/sg/activate" });
    const alertPanel = safeGet("bankAlertPanel");
    if (alertPanel) alertPanel.classList.add("visible");
    const recPanel = safeGet("bankRecPanel");
    if (recPanel) recPanel.classList.add("visible");
  } else {
    err.textContent = "Invalid codes! Try admin/admin/admin/admin";
  }
}
function handleSGButton() {
  if (sgActive) {
    if (confirm("Deactivate Sentinel Grid?")) {
      sgActive = false;
      const sgToggleBtn = safeGet("sgToggleBtn");
      if (sgToggleBtn) sgToggleBtn.classList.remove("on");
      sgToggleBtn.classList.add("off");
      const sgPillText = safeGet("sgPillText");
      if (sgPillText) sgPillText.textContent = "SENTINEL-GRID OFF";
      const hackSgIndicator = safeGet("hackSgIndicator");
      if (hackSgIndicator) hackSgIndicator.classList.remove("on");
      hackSgIndicator.classList.add("off");
      hackSgIndicator.textContent = "SG: INACTIVE";
      logSecurity("🔴 SENTINEL-GRID DEACTIVATED!", { severity: "WARN" });
      const alertPanel = safeGet("bankAlertPanel");
      if (alertPanel) alertPanel.classList.remove("visible");
      const recPanel = safeGet("bankRecPanel");
      if (recPanel) recPanel.classList.remove("visible");
    }
  } else {
    openSgModal();
  }
}
document.addEventListener("DOMContentLoaded", function() {
  const sgBtn = safeGet("sgToggleBtn");
  if (sgBtn) {
    sgBtn.style.display = "none";
  }
});
