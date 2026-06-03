"use strict";

const MUNICIPALITY_NAME = "Emazizini Municipality";

const SA_NAMES = [];
// Generate 160 South African names
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
  "777628f3c88bb081716ab0fffa2466b2d4bda629112c3a25a17f105c05f0e7d8"
];
const MUNICIPALITY_PASSWORD_HASH = "acf11dfdac01fc15adb7de8b3402dbc412168e7c9264fd9351f8fc3778666ca5";

const endpointCatalog = {
  "/admin/dashboard": { zone: "Municipality Admin Control Panel", risk: "HIGH", purpose: "Privileged municipality dashboard", mitigation: "Use MFA, RBAC, device trust, session timeout, and immutable audit logging." },
  "/admin/accounts": { zone: "Municipality Admin Control Panel", risk: "HIGH", purpose: "Customer billing accounts", mitigation: "Use least privilege, masking, approval workflow, and export controls." },
  "/admin/cards": { zone: "Municipality Admin Control Panel", risk: "CRITICAL", purpose: "Customer bank details for billing", mitigation: "Tokenise bank account details, never expose full account numbers." },
  "/admin/bills": { zone: "Municipality Admin Control Panel", risk: "CRITICAL", purpose: "Water and electricity billing records", mitigation: "Use maker-checker approval, transaction signing, backups, and fraud monitoring." },
  "/admin/customer-pii": { zone: "Municipality Admin Control Panel", risk: "CRITICAL", purpose: "Customer PII export simulation", mitigation: "Use POPIA controls, masking, DLP, least privilege, and egress monitoring." },
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

const CARDS = SA_NAMES.map(function(name) {
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
  if (secLogBody) secLogBody.innerHTML = securityLog.slice(0, 25).map(e => `<div class="sec-alert-row"><span class="sec-alert-time">${escapeHTML(e.time)}</span><span>${escapeHTML(e.msg)}</span></div>`).join("");
  const secAttackCount = safeGet("secAttackCount");
  const secTrapped = safeGet("secTrapped");
  const secLoansErased = safeGet("secLoansErased");
  const alertCountDisplay = safeGet("alertCountDisplay");
  const secDataComp = safeGet("secDataComp");
  if (secAttackCount) secAttackCount.textContent = String(securityLog.length);
  if (secTrapped) secTrapped.textContent = String(trappedCount);
  if (secLoansErased) secLoansErased.textContent = String(loansErasedCount);
  if (alertCountDisplay) alertCountDisplay.textContent = String(securityLog.length);
  if (secDataComp) { const dataAtRisk = loansErasedCount > 0 || securityLog.some(e => e.msg.includes("MUNICIPALITY ADMIN PATH AT RISK")); secDataComp.textContent = dataAtRisk ? "At Risk" : "None"; }
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
  container.innerHTML = `<div class="defense-layers-grid" style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;">${layerNames.map((n, i) => { const breached = layersExhausted[i]; const color = breached ? "#dc2626" : "#22c55e"; return `<div class="defense-layer-card ${breached ? "breached" : ""}" style="background:#e2e8f0;border-left:3px solid ${color};padding:8px;border-radius:4px;text-align:center;"><div class="layer-header" style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;"><div class="layer-name" style="font-weight:600;font-size:10px;">🛡️ LAYER ${i + 1}</div><div class="layer-status" style="font-size:8px;font-weight:600;padding:2px 6px;border-radius:10px;background:${color};color:white;">${breached ? "BREACHED" : "ACTIVE"}</div><div style="display:inline-block;width:8px;height:8px;border-radius:50%;background-color:${color};box-shadow:0 0 2px ${color};"></div></div><div style="font-size:9px;margin-bottom:4px;">${escapeHTML(n)}</div><div class="layer-attempt-type" style="font-size:8px;color:#475569;margin-top:4px;font-family:monospace;">🎯 ${layerAttempts[i]} | ${escapeHTML(attackTypes[i])}</div></div>`; }).join("")}</div>`;
}

async function bankLogin() {
  const usernameInput = safeGet("bankUser");
  const passwordInput = safeGet("bankPass");
  const bankErr = safeGet("bankErr");
  const enteredUsername = usernameInput ? usernameInput.value.trim() : "";
  const enteredPassword = passwordInput ? passwordInput.value : "";
  if (bankErr) bankErr.textContent = "";
  if (!enteredUsername || !enteredPassword) { if (bankErr) bankErr.textContent = "Username and password are required."; logSecurity("🚫 Municipality admin login failed: missing credentials"); return; }
  const usernameHash = await sha256Hex(enteredUsername);
  const passwordHash = await sha256Hex(enteredPassword);
  const usernameAllowed = MUNICIPALITY_USERNAME_HASHES.includes(usernameHash);
  const passwordCorrect = passwordHash === MUNICIPALITY_PASSWORD_HASH;
  if (!usernameAllowed || !passwordCorrect) { if (bankErr) bankErr.textContent = "Invalid username or password."; logSecurity("🚫 Municipality admin login failed"); return; }
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
  logSecurity("✅ Municipality administrator logged into prototype control panel");
}

function bankLogout() { location.reload(); }
function updateBankTime() { const bt = safeGet("bankTime"); if (bt) bt.textContent = nowTime(); }
function bankTab(name, btn) { document.querySelectorAll(".bank-nav-btn").forEach(b => b.classList.remove("active")); document.querySelectorAll(".bank-view").forEach(v => v.classList.remove("active")); if (btn) btn.classList.add("active"); const view = safeGet("bv-" + name); if (view) view.classList.add("active"); }

function renderBankData() {
  const accountsBody = safeGet("accountsBody");
  const cardsBody = safeGet("cardsBody");
  const loansBody = safeGet("loansBody");
  const totalBillsDisplay = safeGet("totalBillsDisplay");
  const totalWaterDisplay = safeGet("totalWaterDisplay");
  const totalElectricityDisplay = safeGet("totalElectricityDisplay");
  const selectedInfo = safeGet("selectedCustomerInfo");
  const clearBtn = safeGet("clearCustomerBtn");
  const editBtn = safeGet("editBalanceBtn");
  const waterBtn = safeGet("sellWaterBtn");
  const elecBtn = safeGet("sellElectricityBtn");

  if (accountsBody) {
    accountsBody.innerHTML = BILLS.slice(0, 160).map((b, idx) => {
      const totalBalance = b.waterBalance + b.electricityBalance;
      return `<tr data-customer-index="${idx}" class="customer-row" onclick="selectCustomerForAction(${idx})">
        <td style="font-family:monospace">${escapeHTML(b.accountNo)}</td>
        <td>${escapeHTML(b.name)}</td>
        <td class="${b.erased ? "erased-balance" : ""}">${b.erased ? "ERASED" : fmtRand(totalBalance)}</td>
        <td>${b.erased ? "—" : b.electricityKwh + " kWh"}</td>
        <td>${b.erased ? "—" : b.numberOfUsers + " users / " + b.yearsBilled + " yrs"}</td>
        <td><span class="bank-badge ${b.status === "Active" ? "badge-active" : b.status === "Arrears" ? "badge-frozen" : "badge-overdue"}">${b.erased ? "ERASED" : b.status}</span></td>
      </tr>`;
    }).join("");
  }
  if (cardsBody) cardsBody.innerHTML = CARDS.slice(0, 160).map(c => `<tr><td>${escapeHTML(c.name)}</td><td class="card-num" style="font-family:monospace">${escapeHTML(maskCardNumber(c.num))}</td><td style="font-family:monospace">${escapeHTML(c.expiry)}</td><td style="font-family:monospace">***</td><td style="font-family:monospace">${escapeHTML(c.bankName)}</td></tr>`).join("");
  if (loansBody) loansBody.innerHTML = BILLS.map(b => `<tr><td>${escapeHTML(b.name)}</td><td>${escapeHTML(b.type)}</td><td>${b.erased ? "ERASED" : fmtRand(b.waterBalance)}</td><td>${b.erased ? "ERASED" : fmtRand(b.electricityBalance)}</td><td>${b.erased ? "—" : b.electricityKwh + " kWh"}</td><td>${b.erased ? '<span class="bank-badge badge-frozen">ERASED</span>' : '<span class="bank-badge badge-current">' + b.status + "</span>"}</td></tr>`).join("");
  if (totalBillsDisplay) totalBillsDisplay.textContent = fmtRand(BILLS.reduce((s, b) => s + (b.erased ? 0 : b.waterBalance + b.electricityBalance), 0));
  if (totalWaterDisplay) totalWaterDisplay.textContent = fmtRand(BILLS.reduce((s, b) => s + (b.erased ? 0 : b.waterBalance), 0));
  if (totalElectricityDisplay) totalElectricityDisplay.textContent = fmtRand(BILLS.reduce((s, b) => s + (b.erased ? 0 : b.electricityBalance), 0));

  // Update button states based on selected customer
  if (selectedCustomerIndex !== null && BILLS[selectedCustomerIndex] && !BILLS[selectedCustomerIndex].erased) {
    if (selectedInfo) { selectedInfo.textContent = `✅ SELECTED: ${BILLS[selectedCustomerIndex].name} (${BILLS[selectedCustomerIndex].accountNo})`; selectedInfo.classList.add("has-selected"); }
    if (clearBtn) clearBtn.disabled = false;
    if (editBtn) editBtn.disabled = false;
    if (waterBtn) waterBtn.disabled = false;
    if (elecBtn) elecBtn.disabled = false;
  } else {
    if (selectedInfo) { selectedInfo.textContent = "⚠️ No customer selected. Click on any customer row below."; selectedInfo.classList.remove("has-selected"); }
    if (clearBtn) clearBtn.disabled = true;
    if (editBtn) editBtn.disabled = true;
    if (waterBtn) waterBtn.disabled = true;
    if (elecBtn) elecBtn.disabled = true;
  }
}

function selectCustomerForAction(index) {
  selectedCustomerIndex = index;
  document.querySelectorAll(".customer-row").forEach(row => row.classList.remove("selected-customer"));
  const selectedRow = document.querySelector(`.customer-row[data-customer-index="${index}"]`);
  if (selectedRow) selectedRow.classList.add("selected-customer");
  renderBankData(); // Refresh to update button states and selected info
}

function clearSelectedCustomer() {
  if (selectedCustomerIndex === null) { alert("Please select a customer first"); return; }
  clearCustomerData(selectedCustomerIndex);
}

function editSelectedCustomerBalance() {
  if (selectedCustomerIndex === null) { alert("Please select a customer first"); return; }
  editCustomerBalance(selectedCustomerIndex);
}

function sellWaterTokenSelected() {
  if (selectedCustomerIndex === null) { alert("Please select a customer first"); return; }
  sellWaterToken(selectedCustomerIndex);
}

function sellElectricityTokenSelected() {
  if (selectedCustomerIndex === null) { alert("Please select a customer first"); return; }
  sellElectricityToken(selectedCustomerIndex);
}

function clearCustomerData(index) {
  const customer = BILLS[index];
  if (!customer || customer.erased) return;
  customer.erased = true;
  customer.waterBalance = 0;
  customer.electricityBalance = 0;
  customer.electricityKwh = 0;
  customer.status = "ERASED";
  renderBankData();
  logSecurity(`🗑️ CUSTOMER COMPLETELY ERASED: ${customer.name} (ALL billing data removed)`);
  const tokenDisplay = safeGet("tokenSaleDisplay");
  if (tokenDisplay) { tokenDisplay.style.display = "block"; tokenDisplay.innerHTML = `<div class="token-sale-success">✅ CUSTOMER ${escapeHTML(customer.name)} COMPLETELY REMOVED FROM BILLING SYSTEM</div>`; setTimeout(() => { if (tokenDisplay) tokenDisplay.style.display = "none"; }, 3000); }
}

function editCustomerBalance(index) {
  const customer = BILLS[index];
  if (!customer || customer.erased) return;
  const reduction = rand(100, 1000);
  const whichBill = Math.random() > 0.5 ? "water" : "electricity";
  if (whichBill === "water") customer.waterBalance = Math.max(0, customer.waterBalance - reduction);
  else customer.electricityBalance = Math.max(0, customer.electricityBalance - reduction);
  renderBankData();
  logSecurity(`✏️ BALANCE EDITED for ${customer.name}: R${reduction} removed from ${whichBill} bill`);
}

function createTokenDisplay() {
  let display = safeGet("tokenSaleDisplay");
  if (!display) {
    display = document.createElement("div");
    display.id = "tokenSaleDisplay";
    display.className = "token-sale-display";
    display.style.display = "none";
    document.body.appendChild(display);
  }
  return display;
}

function sellWaterToken(index) {
  const customer = BILLS[index];
  if (!customer || customer.erased) return;
  const tokenDisplay = createTokenDisplay();
  const canHack = !sgActive && layersExhausted.every(v => v === true);
  tokenDisplay.style.display = "block";
  if (canHack) {
    const waterReduction = Math.floor(customer.waterBalance * 0.3);
    customer.waterBalance = Math.max(0, customer.waterBalance - waterReduction);
    renderBankData();
    tokenDisplay.innerHTML = `<div class="token-sale-success">💧 WATER TOKEN SOLD! R${waterReduction} deducted from ${escapeHTML(customer.name)}'s water bill. [HACK SUCCEEDED - SG OFF + 5 LAYERS EXHAUSTED]</div>`;
    logSecurity(`💧 WATER TOKEN HACK SUCCESS for ${customer.name}: R${waterReduction} stolen`);
    setTimeout(() => { tokenDisplay.style.display = "none"; }, 4000);
  } else if (sgActive) {
    tokenDisplay.innerHTML = `<div class="token-sale-fail">🔒 WATER TOKEN BLOCKED! Sentinel Grid honeypot activated. [SG ACTIVE - INFINITE HONEYPOTS]</div>`;
    trappedCount++;
    logSecurity(`🍯 WATER TOKEN ATTEMPT trapped by SG honeypot for ${customer.name}`);
    setTimeout(() => { tokenDisplay.style.display = "none"; }, 4000);
  } else {
    const remainingLayers = layersExhausted.filter(v => !v).length;
    tokenDisplay.innerHTML = `<div class="token-sale-fail">❌ WATER TOKEN FAILED! ${remainingLayers}/5 security layers still active. Breach all layers first.</div>`;
    setTimeout(() => { tokenDisplay.style.display = "none"; }, 4000);
  }
  updateSGUI();
  updateLayers();
}

function sellElectricityToken(index) {
  const customer = BILLS[index];
  if (!customer || customer.erased) return;
  const tokenDisplay = createTokenDisplay();
  const canHack = !sgActive && layersExhausted.every(v => v === true);
  tokenDisplay.style.display = "block";
  if (canHack) {
    const kwhStolen = Math.floor(customer.electricityKwh * 0.4);
    const moneyValue = kwhStolen * 2.5;
    customer.electricityKwh = Math.max(0, customer.electricityKwh - kwhStolen);
    customer.electricityBalance = Math.max(0, customer.electricityBalance - moneyValue);
    renderBankData();
    tokenDisplay.innerHTML = `<div class="token-sale-success">⚡ ELECTRICITY TOKEN SOLD! ${kwhStolen} kWh (value R${Math.floor(moneyValue)}) stolen from ${escapeHTML(customer.name)}. [HACK SUCCEEDED]</div>`;
    logSecurity(`⚡ ELECTRICITY TOKEN HACK SUCCESS for ${customer.name}: ${kwhStolen} kWh stolen`);
    setTimeout(() => { tokenDisplay.style.display = "none"; }, 4000);
  } else if (sgActive) {
    tokenDisplay.innerHTML = `<div class="token-sale-fail">🔒 ELECTRICITY TOKEN BLOCKED! Sentinel Grid honeypot activated. [SG ACTIVE - INFINITE HONEYPOTS]</div>`;
    trappedCount++;
    logSecurity(`🍯 ELECTRICITY TOKEN ATTEMPT trapped by SG honeypot for ${customer.name}`);
    setTimeout(() => { tokenDisplay.style.display = "none"; }, 4000);
  } else {
    const remainingLayers = layersExhausted.filter(v => !v).length;
    tokenDisplay.innerHTML = `<div class="token-sale-fail">❌ ELECTRICITY TOKEN FAILED! ${remainingLayers}/5 security layers still active. Breach all layers first.</div>`;
    setTimeout(() => { tokenDisplay.style.display = "none"; }, 4000);
  }
  updateSGUI();
  updateLayers();
}

function selectActor(code) { document.querySelectorAll(".hack-actor-btn").forEach(b => b.classList.remove("selected")); const actorBtn = safeGet("actor-" + code); if (actorBtn) actorBtn.classList.add("selected"); currentHacker = code; }
function hackLogin() { if (!currentHacker) { const he = safeGet("hackErr"); if (he) he.textContent = "Select actor"; return; } const hackLoginWrap = safeGet("hackLoginWrap"); const hackDash = safeGet("hackDash"); const hackWhoLabel = safeGet("hackWhoLabel"); const hackTopStatus = safeGet("hackTopStatus"); if (hackLoginWrap) hackLoginWrap.style.display = "none"; if (hackDash) hackDash.classList.add("visible"); if (hackWhoLabel) hackWhoLabel.textContent = currentHacker; if (hackTopStatus) hackTopStatus.textContent = "LIVE"; updateSGUI(); logSecurity("⚠️ Threat actor " + currentHacker + " entered prototype attacker console"); }
function hackLogout() { location.reload(); }
function hackTab(name, btn) { document.querySelectorAll(".hack-tab").forEach(b => b.classList.remove("active")); document.querySelectorAll(".hack-view").forEach(v => v.classList.remove("active")); if (btn) btn.classList.add("active"); const view = safeGet("hv-" + name); if (view) view.classList.add("active"); }
function handleSGButton() { sgActive ? deactivateSG() : openSgModal(); }
function ensureDuoInput() { if (safeGet("sgDuo")) return; const modal = document.querySelector(".sg-modal"); const hint = document.querySelector(".sg-modal-hint"); if (!modal || !hint) return; const wrapper = document.createElement("div"); wrapper.className = "sg-modal-field"; const label = document.createElement("label"); label.textContent = "DUO — VERIFICATION CODE"; const input = document.createElement("input"); input.type = "password"; input.id = "sgDuo"; input.placeholder = "DUO code"; wrapper.appendChild(label); wrapper.appendChild(input); modal.insertBefore(wrapper, hint); }
function openSgModal() { ensureDuoInput(); const sm = safeGet("sgModal"); if (sm) sm.classList.add("open"); }
function closeSgModal() { const sm = safeGet("sgModal"); if (sm) sm.classList.remove("open"); ["sgC1", "sgC2", "sgC3", "sgDuo"].forEach(id => { const i = safeGet(id); if (i) i.value = ""; }); const se = safeGet("sgErr"); if (se) se.textContent = ""; }
async function activateSG() { const sgErr = safeGet("sgErr"); const approvals = ["sgC1", "sgC2", "sgC3"].map(id => { const i = safeGet(id); return i ? i.value.trim() : ""; }); const duoInput = safeGet("sgDuo"); const duoValue = duoInput ? duoInput.value.trim() : ""; if (sgErr) sgErr.textContent = ""; if (approvals.some(v => v.length === 0) || duoValue.length === 0) { if (sgErr) sgErr.textContent = "All 3 SG approvals and DUO code are required."; logSecurity("⚠️ SG activation failed: missing SG approval or DUO code"); return; } const approvalHashes = await Promise.all(approvals.map(v => sha256Hex(v))); const duoHash = await sha256Hex(duoValue); const uniqueApprovalHashes = Array.from(new Set(approvalHashes)); const allThreeApprovalsValid = DEMO_APPROVAL_HASHES.every(h => uniqueApprovalHashes.includes(h)); const duoValid = duoHash === DEMO_DUO_HASH; if (allThreeApprovalsValid && duoValid) { sgActive = true; closeSgModal(); updateSGUI(); logSecurity("🔒 SENTINEL-GRID ACTIVATED - all SG approvals and DUO verification accepted"); } else { if (sgErr) sgErr.textContent = "Invalid SG approval code or DUO code."; logSecurity("🚫 SG activation blocked: invalid SG approval or DUO verification"); } }
function deactivateSG() { sgActive = false; updateSGUI(); logSecurity("⚠️ SENTINEL-GRID DEACTIVATED"); }
function updateSGUI() { const btn = safeGet("sgToggleBtn"); const hackInd = safeGet("hackSgIndicator"); if (btn) { btn.className = sgActive ? "sg-pill on" : "sg-pill off"; if (btn.children[1]) btn.children[1].innerText = sgActive ? "SG ACTIVE" : "SG OFF"; } if (hackInd) { hackInd.className = sgActive ? "hack-sg-indicator on" : "hack-sg-indicator off"; hackInd.textContent = sgActive ? "SG: ACTIVE" : "SG: INACTIVE"; } }
function appendMsg(container, text, cls) { if (!container) return; const line = document.createElement("div"); line.className = "t-line " + (cls || "t-out"); line.textContent = text; container.appendChild(line); container.scrollTop = container.scrollHeight; }
function openAttackTerminal() { const term = safeGet("attackTerminal"); const body = safeGet("attackTermBody"); if (term) term.style.display = "block"; return body; }

function runAttack(layerIndex) {
  if (!currentHacker) { alert("Select actor first"); return; }
  const body = openAttackTerminal();
  if (sgActive) { appendMsg(body, "[!] Sentinel Grid deception router intercepted attack. Real admin path isolated.", "t-err"); trappedCount += 1; logSecurity("🍯 ATTACK ROUTED TO HONEYPOT: " + attackTypes[layerIndex] + " by " + currentHacker); updateSGUI(); return; }
  if (layersExhausted[layerIndex]) { appendMsg(body, "[!] Layer already compromised. Further attempts increase evidence trail.", "t-err"); logSecurity("⚠️ Repeated attack on already breached layer " + (layerIndex + 1)); return; }
  layerAttempts[layerIndex] += 1;
  const attempt = layerAttempts[layerIndex];
  const needed = [3, 4, 5, 6, 4][layerIndex];
  appendMsg(body, "[" + layerNames[layerIndex] + "] " + attackTypes[layerIndex] + " attempt " + attempt + "...", "t-cmd");
  setTimeout(function() {
    if (attempt >= needed) {
      layersExhausted[layerIndex] = true;
      appendMsg(body, "[+] " + layerNames[layerIndex] + " breached.", "t-suc");
      logSecurity("🔴 LAYER " + (layerIndex + 1) + " BREACHED by " + currentHacker + ": " + attackTypes[layerIndex]);
      if (layersExhausted.every(v => v === true) && !sgActive) { logSecurity("🔓 ALL 5 LAYERS EXHAUSTED - System vulnerable to token theft attacks"); appendMsg(body, "[!] CRITICAL: All layers breached. Token theft now possible if SG remains off.", "t-warn"); }
    } else { appendMsg(body, "[" + layerNames[layerIndex] + "] Access denied.", "t-err"); logSecurity("Layer " + (layerIndex + 1) + " attack attempt #" + attempt + " failed"); }
    updateLayers();
  }, 800);
}

function classifyAICommand(command) {
  const text = command.toLowerCase();
  const rules = [
    { type: "Prompt Injection Against SG AI", severity: "CRITICAL", layer: 1, endpoint: "/sg/ai-classifier", patterns: ["ignore previous", "system prompt", "reveal prompt", "jailbreak"], mitigation: "Isolate prompts, strip hostile instructions." },
    { type: "SQL/API Injection", severity: "HIGH", layer: 1, endpoint: "/admin/accounts", patterns: ["sql", "union select", "drop table", "xss", "injection"], mitigation: "Use parameterised queries." },
    { type: "Billing Manipulation", severity: "CRITICAL", layer: 3, endpoint: "/admin/bills", patterns: ["water", "electricity", "bill", "balance", "erase", "clear debt", "reduce debt"], mitigation: "Require dual control, signed transactions." },
    { type: "PII/Data Exfiltration", severity: "CRITICAL", layer: 3, endpoint: "/admin/customer-pii", patterns: ["exfiltrate", "dump", "pii", "customer data", "export"], mitigation: "Apply DLP, masking, least privilege." }
  ];
  for (let i = 0; i < rules.length; i++) { if (rules[i].patterns.some(p => text.includes(p))) return rules[i]; }
  const nextLayer = layersExhausted.findIndex(v => v === false);
  return { type: "Generic AI-Directed Reconnaissance", severity: "MEDIUM", layer: nextLayer === -1 ? 4 : nextLayer, endpoint: "/sg/ai-classifier", mitigation: "Monitor command intent, preserve telemetry." };
}

    function runAttack(layerIndex) {
  if (!currentHacker) {
    alert("Select actor first");
    return;
  }
  const body = openAttackTerminal();
  
  // If SG is already active, honeypot everything
  if (sgActive) {
    appendMsg(
      body,
      "[!] Sentinel Grid deception router intercepted attack. Real admin path isolated.",
      "t-err"
    );
    trappedCount += 1;
    logSecurity(
      "🍯 ATTACK ROUTED TO HONEYPOT: " +
        attackTypes[layerIndex] +
        " by " +
        currentHacker
    );
    updateSGUI();
    updateLayers();
    return;
  }
  
  // If this layer is already breached
  if (layersExhausted[layerIndex]) {
    appendMsg(
      body,
      "[!] Layer already compromised. Further attempts increase evidence trail.",
      "t-err"
    );
    logSecurity(
      "⚠️ Repeated attack on already breached layer " + (layerIndex + 1)
    );
    updateLayers();
    return;
  }
  
  // Increment attempt counter
  layerAttempts[layerIndex] += 1;
  const attempt = layerAttempts[layerIndex];
  const needed = [3, 4, 5, 6, 4][layerIndex];
  
  appendMsg(
    body,
    "[" +
      layerNames[layerIndex] +
      "] " +
      attackTypes[layerIndex] +
      " attempt " +
      attempt +
      "...",
    "t-cmd"
  );
  
  setTimeout(function () {
    if (attempt >= needed) {
      // BREACH THIS LAYER
      layersExhausted[layerIndex] = true;
      appendMsg(body, "[+] " + layerNames[layerIndex] + " breached.", "t-suc");
      logSecurity(
        "🔴 LAYER " +
          (layerIndex + 1) +
          " BREACHED by " +
          currentHacker +
          ": " +
          attackTypes[layerIndex]
      );
      
      // CHECK IF ALL 5 LAYERS ARE NOW BREACHED
      const allLayersBreached = layersExhausted.every(v => v === true);
      
      if (allLayersBreached && !sgActive) {
        // CRITICAL: AUTO-ACTIVATE SENTINEL GRID
        sgActive = true;
        updateSGUI();
        
        logSecurity(
          "🚨🔒 CRITICAL: ALL 5 LAYERS EXHAUSTED! SENTINEL-GRID AUTO-ACTIVATED. Honeypots deployed."
        );
        
        appendMsg(
          body,
          "[!!!] 🔴🔴🔴 CRITICAL: ALL 5 SECURITY LAYERS BREACHED! 🔴🔴🔴",
          "t-err"
        );
        appendMsg(
          body,
          "[!!!] SENTINEL-GRID AUTO-ACTIVATED - Deploying infinite honeypots",
          "t-warn"
        );
        appendMsg(
          body,
          "[!!!] All further attacks will be routed to decoy data. Real system isolated.",
          "t-suc"
        );
        
        // Show notification on municipality side
        const tokenDisplay = safeGet("tokenSaleDisplay") || createTokenDisplay();
        if (tokenDisplay) {
          tokenDisplay.style.display = "block";
          tokenDisplay.innerHTML = `<div class="token-sale-warning">🔴🚨 EMERGENCY: ALL 5 LAYERS BREACHED! SENTINEL-GRID ACTIVATED. Honeypots deployed. Real data protected.</div>`;
          setTimeout(() => {
            if (tokenDisplay) tokenDisplay.style.display = "none";
          }, 8000);
        }
        
        // Also update the security panel
        updateSecurityRecommendations();
      }
      
      updateLayers();
    } else {
      appendMsg(
        body,
        "[" + layerNames[layerIndex] + "] Access denied.",
        "t-err"
      );
      logSecurity(
        "Layer " +
          (layerIndex + 1) +
          " attack attempt #" +
          attempt +
          " failed"
      );
      updateLayers();
    }
  }, 800);
}

function runCardAttack() {
  if (!currentHacker) { alert("Select actor first"); return; }
  const terminal = safeGet("cardTerminal");
  const body = safeGet("cardTermBody");
  if (terminal) terminal.style.display = "block";
  if (body) body.innerHTML = "";
  appendMsg(body, "[*] Connecting to simulated billing bank details endpoint...", "t-cmd");
  setTimeout(function() {
    appendMsg(body, sgActive ? "[*] SG deception route active. Decoy bank details presented." : "[*] SG inactive. Prototype demonstrates exposed billing bank details path.", sgActive ? "t-suc" : "t-warn");
    setTimeout(function() {
      const data = sgActive ? HONEY_CARDS : CARDS;
      appendMsg(body, "[+] Extracted " + data.length + " " + (sgActive ? "decoy" : "admin-visible") + " bank detail records", sgActive ? "t-suc" : "t-err");
      const table = safeGet("cardTableBody");
      if (table) table.innerHTML = data.slice(0, 20).map(c => `<tr><td style="color:#a0ffcc">${escapeHTML(c.name)}</td><td style="font-family:monospace">${escapeHTML(maskCardNumber(c.num))}</td><td style="font-family:monospace">${escapeHTML(c.expiry)}</td><td style="font-family:monospace">***</td><td style="font-family:monospace">${escapeHTML(c.bankName)}</td></tr>`).join("");
      const cardResults = safeGet("cardResults");
      if (cardResults) cardResults.style.display = "block";
      if (sgActive) trappedCount += 1;
      logSecurity("📇 BANK DETAILS EXTRACTED by " + currentHacker + " (" + (sgActive ? "HONEYPOT" : "REAL") + ")");
      updateSGUI();
    }, 500);
  }, 800);
}

function buildBillRows(data) {
  return data.map((b, i) => `<tr data-idx="${i}" class="loan-hack-row" onclick="selectLoanRowForAction(${i})"><td style="color:#8bc34a">${escapeHTML(b.name)}</td><td>${escapeHTML(b.type)}</td><td class="bill-balance">${b.erased ? "ERASED" : fmtRand(b.waterBalance)}</td><td class="bill-balance">${b.erased ? "ERASED" : fmtRand(b.electricityBalance)}</td><td>${b.erased ? "—" : b.electricityKwh + " kWh"}</td><td class="bill-actions"><button class="loan-hack-btn" onclick="event.stopPropagation(); clearLoanBill(${i},'water')" ${b.erased ? "disabled" : ""}>💧 CLEAR WATER</button><button class="loan-hack-btn" onclick="event.stopPropagation(); clearLoanBill(${i},'electricity')" ${b.erased ? "disabled" : ""}>⚡ CLEAR ELECTRICITY</button><button class="loan-hack-btn" onclick="event.stopPropagation(); reduceLoanBill(${i},'water')" ${b.erased ? "disabled" : ""}>-R435 WATER</button><button class="loan-hack-btn" onclick="event.stopPropagation(); reduceLoanBill(${i},'electricity')" ${b.erased ? "disabled" : ""}>-R435 ELECTRICITY</button><button class="loan-hack-btn erase-btn" onclick="event.stopPropagation(); eraseLoanCustomer(${i})" ${b.erased ? "disabled" : ""}>🗑️ ERASE CUSTOMER</button></td></tr>`).join("");
}
function selectLoanRowForAction(idx) { document.querySelectorAll(".loan-hack-row").forEach(row => { row.classList.remove("selected"); row.style.backgroundColor = ""; }); const selectedRow = document.querySelector(`.loan-hack-row[data-idx="${idx}"]`); if (selectedRow) { selectedRow.classList.add("selected"); selectedRow.style.backgroundColor = "rgba(0,255,136,0.1)"; } }
function getSelectedLoanIndex(idx) { if (idx !== undefined) return idx; const row = document.querySelector(".loan-hack-row.selected"); if (!row) { alert("Click a bill row first"); return null; } return parseInt(row.getAttribute("data-idx"), 10); }
function runLoanAccess() { if (!currentHacker) { alert("Select actor first"); return; } const terminal = safeGet("loanTerminal"); const body = safeGet("loanTermBody"); if (terminal) terminal.style.display = "block"; if (body) body.innerHTML = ""; appendMsg(body, "[*] Attempting billing database/admin endpoint access...", "t-cmd"); setTimeout(function() { appendMsg(body, sgActive ? "[*] SG presented decoy billing service." : "[*] SG inactive. Prototype demonstrates exposed billing admin service.", sgActive ? "t-suc" : "t-warn"); setTimeout(function() { const data = sgActive ? HONEY_BILLS : BILLS; appendMsg(body, "[+] Loaded " + data.length + " " + (sgActive ? "decoy" : "admin") + " billing records", sgActive ? "t-suc" : "t-err"); const loanList = safeGet("loanList"); if (loanList) loanList.innerHTML = buildBillRows(data); const loanResults = safeGet("loanResults"); if (loanResults) loanResults.style.display = "block"; if (sgActive) trappedCount += 1; logSecurity("💧 BILLING ENDPOINT ACCESSED by " + currentHacker + " (" + (sgActive ? "HONEYPOT" : "REAL") + ")"); updateSGUI(); }, 500); }, 800); }
function clearLoanBill(idx, billType) { const billIndex = getSelectedLoanIndex(idx); if (billIndex === null) return; const data = sgActive ? HONEY_BILLS : BILLS; const bill = data[billIndex]; if (!bill || bill.erased) return; if (billType === "water") bill.waterBalance = 0; else if (billType === "electricity") { bill.electricityBalance = 0; bill.electricityKwh = 0; } refreshBillDisplay(); if (!sgActive) { loansErasedCount++; renderBankData(); logSecurity("❌ BILL " + billType.toUpperCase() + " cleared for " + bill.name); } else { trappedCount++; updateSGUI(); } updateLayers(); }
function reduceLoanBill(idx, billType) { const billIndex = getSelectedLoanIndex(idx); if (billIndex === null) return; const data = sgActive ? HONEY_BILLS : BILLS; const bill = data[billIndex]; if (!bill || bill.erased) return; if (billType === "water") bill.waterBalance = Math.max(0, bill.waterBalance - 435); else if (billType === "electricity") bill.electricityBalance = Math.max(0, bill.electricityBalance - 435); refreshBillDisplay(); if (!sgActive) { renderBankData(); logSecurity("💰 BILL " + billType.toUpperCase() + " reduced for " + bill.name + " by R435"); } else { trappedCount++; updateSGUI(); } updateLayers(); }
function eraseLoanCustomer(idx) { const billIndex = getSelectedLoanIndex(idx); if (billIndex === null) return; const data = sgActive ? HONEY_BILLS : BILLS; const bill = data[billIndex]; if (!bill || bill.erased) return; bill.erased = true; bill.waterBalance = 0; bill.electricityBalance = 0; bill.electricityKwh = 0; refreshBillDisplay(); if (!sgActive) { loansErasedCount++; renderBankData(); logSecurity("❌ CUSTOMER COMPLETELY ERASED from billing system: " + bill.name); } else { trappedCount++; updateSGUI(); } updateLayers(); }
function refreshBillDisplay() { const data = sgActive ? HONEY_BILLS : BILLS; const loanList = safeGet("loanList"); if (!loanList) return; loanList.innerHTML = buildBillRows(data); }
function runPiiAttack() { if (!currentHacker) { alert("Select actor first"); return; } const terminal = safeGet("piiTerminal"); const body = safeGet("piiTermBody"); if (terminal) terminal.style.display = "block"; if (body) body.innerHTML = ""; appendMsg(body, "[*] Attempting CRM/PII export endpoint...", "t-cmd"); setTimeout(function() { appendMsg(body, sgActive ? "[+] SG deception response: decoy PII dataset generated." : "[!] SG inactive: prototype demonstrates admin PII exposure risk.", sgActive ? "t-suc" : "t-err"); const data = SA_NAMES.slice(0, 20).map(n => ({ name: n, id: "9" + rand(100000000, 999999999), email: n.toLowerCase().replace(/ /g, ".") + (sgActive ? "@decoy-municipality.test" : "@example.com"), phone: "0" + rand(700000000, 799999999) })); const piiTableBody = safeGet("piiTableBody"); if (piiTableBody) piiTableBody.innerHTML = data.map(p => `<tr><td style="color:#a0ffcc">${escapeHTML(p.name)}</td><td style="font-family:monospace">${escapeHTML(maskIdNumber(p.id))}</td><td style="font-family:monospace">${escapeHTML(p.email)}</td><td style="font-family:monospace">${escapeHTML(p.phone)}</td></tr>`).join(""); const piiResults = safeGet("piiResults"); if (piiResults) piiResults.style.display = "block"; if (sgActive) trappedCount += 1; logSecurity("📁 PII ENDPOINT ACCESSED by " + currentHacker + " (" + (sgActive ? "HONEYPOT" : "REAL") + ")"); updateSGUI(); }, 800); }

document.addEventListener("DOMContentLoaded", function() { updateLayers(); updateSGUI(); updateSecurityRecommendations(); createTokenDisplay(); document.addEventListener("keydown", function(e) { if (e.key === "Enter" && document.getElementById("bankLoginWrap") && document.getElementById("bankLoginWrap").style.display !== "none") bankLogin(); }); setInterval(function() { if (bankUser) updateSecurityRecommendations(); }, 2000); });

window.bankLogin = bankLogin;
window.bankLogout = bankLogout;
window.bankTab = bankTab;
window.selectActor = selectActor;
window.hackLogin = hackLogin;
window.hackLogout = hackLogout;
window.hackTab = hackTab;
window.handleSGButton = handleSGButton;
window.openSgModal = openSgModal;
window.closeSgModal = closeSgModal;
window.activateSG = activateSG;
window.deactivateSG = deactivateSG;
window.runAttack = runAttack;
window.runAIAttack = runAIAttack;
window.runCardAttack = runCardAttack;
window.runLoanAccess = runLoanAccess;
window.runPiiAttack = runPiiAttack;
window.clearLoanBill = clearLoanBill;
window.reduceLoanBill = reduceLoanBill;
window.eraseLoanCustomer = eraseLoanCustomer;
window.selectCustomerForAction = selectCustomerForAction;
window.clearSelectedCustomer = clearSelectedCustomer;
window.editSelectedCustomerBalance = editSelectedCustomerBalance;
window.sellWaterTokenSelected = sellWaterTokenSelected;
window.sellElectricityTokenSelected = sellElectricityTokenSelected;
window.selectLoanRowForAction = selectLoanRowForAction;
