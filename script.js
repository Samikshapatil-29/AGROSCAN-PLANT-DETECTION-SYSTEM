/**
 * script.js – AgroScan frontend logic
 * Handles: camera, capture, upload, predict, stats, sidebar
 */

// ── Sidebar toggle (mobile) ───────────────────────────────────────────────
function toggleSidebar() {
  document.getElementById("sidebar")?.classList.toggle("open");
  document.getElementById("sidebar-overlay")?.classList.toggle("open");
}

// ── Only run scanner logic on the scan page ───────────────────────────────
const video      = document.getElementById("video");
const canvas     = document.getElementById("canvas");
const snapshot   = document.getElementById("snapshot");
const btnCapture = document.getElementById("btn-capture");
const btnRetake  = document.getElementById("btn-retake");
const btnAnalyse = document.getElementById("btn-analyse");
const fileInput  = document.getElementById("file-input");
const resultCard = document.getElementById("result-card");
const spinner    = document.getElementById("spinner");

if (video) {
  // ── Start camera ──────────────────────────────────────────────────────
  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
        audio: false,
      });
      video.srcObject = stream;

      // Add animated scan line once video is playing
      video.addEventListener("playing", () => {
        const overlay = document.getElementById("camera-overlay");
        if (overlay && !overlay.querySelector(".scan-line")) {
          const line = document.createElement("div");
          line.className = "scan-line";
          document.querySelector(".scan-frame")?.appendChild(line);
        }
      }, { once: true });

    } catch (err) {
      console.warn("Camera unavailable:", err);
      document.querySelector(".camera-container").style.display = "none";
      btnCapture.style.display = "none";
    }
  }

  startCamera();

  // ── Capture frame ─────────────────────────────────────────────────────
  function captureFrame() {
    canvas.width  = video.videoWidth  || 640;
    canvas.height = video.videoHeight || 480;
    canvas.getContext("2d").drawImage(video, 0, 0);

    // Flash effect
    const flash = document.createElement("div");
    flash.style.cssText = `
      position:absolute;inset:0;background:white;
      border-radius:16px;opacity:0.8;pointer-events:none;
      animation:flashOut 0.3s ease forwards;
    `;
    document.querySelector(".camera-container").appendChild(flash);
    setTimeout(() => flash.remove(), 350);

    capturedDataUrl = canvas.toDataURL("image/jpeg", 0.9);
    showSnapshot(capturedDataUrl);
  }

  // ── Retake ────────────────────────────────────────────────────────────
  function retake() {
    capturedDataUrl = null;
    snapshot.style.display = "none";
    document.querySelector(".camera-container").style.display = "block";
    btnCapture.style.display = "inline-flex";
    btnRetake.style.display  = "none";
    btnAnalyse.style.display = "none";
    hideResult();
  }

  // ── File upload ───────────────────────────────────────────────────────
  function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => showSnapshot(ev.target.result);
    reader.readAsDataURL(file);
  }

  // ── Show snapshot ─────────────────────────────────────────────────────
  function showSnapshot(dataUrl) {
    capturedDataUrl = dataUrl;
    snapshot.src = dataUrl;
    snapshot.style.display = "block";
    document.querySelector(".camera-container").style.display = "none";
    btnCapture.style.display = "none";
    btnRetake.style.display  = "inline-flex";
    btnAnalyse.style.display = "inline-flex";
    btnAnalyse.disabled      = false;
    hideResult();
    hideInvalid();
  }

  // ── Analyse ───────────────────────────────────────────────────────────
  async function analyse() {
    if (!capturedDataUrl) return;
    showSpinner(true);
    hideResult();
    hideInvalid();

    try {
      const res  = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: capturedDataUrl }),
      });
      const data = await res.json();

      if (res.status === 422 || data.error) {
        // Invalid image — show error card, do NOT show result
        showInvalid();
      } else {
        showResult(data);
        loadStats();
      }
    } catch {
      alert("Cannot reach the server. Make sure Flask is running.");
    } finally {
      showSpinner(false);
    }
  }

  // ── Show result ───────────────────────────────────────────────────────
  function showResult(data) {
    const isHealthy = data.status === "Healthy";

    // Plant emoji map
    const plantEmoji = {
      "Apple":       "🍎", "Blueberry":  "🫐", "Cherry":    "🍒",
      "Corn":        "🌽", "Grape":      "🍇", "Orange":    "🍊",
      "Peach":       "🍑", "Pepper":     "🫑", "Potato":    "🥔",
      "Raspberry":   "🍓", "Soybean":    "🌱", "Squash":    "🎃",
      "Strawberry":  "🍓", "Tomato":     "🍅",
    };
    const emoji = plantEmoji[data.plant] || "🌿";

    // ── Plant banner ──────────────────────────────────────────────────
    document.getElementById("plant-banner-emoji").textContent = emoji;
    document.getElementById("plant-banner-name").textContent  = data.plant;
    const bannerBadge = document.getElementById("plant-banner-badge");
    bannerBadge.textContent = isHealthy ? "✅ Healthy" : "⚠️ Diseased";
    bannerBadge.className   = "plant-banner-badge " + (isHealthy ? "healthy" : "diseased");

    // ── Status & disease ──────────────────────────────────────────────
    document.getElementById("result-emoji").textContent   = isHealthy ? "✅" : "⚠️";
    const statusEl = document.getElementById("result-status");
    statusEl.textContent = data.status;
    statusEl.className   = "result-status " + (isHealthy ? "healthy" : "diseased");
    document.getElementById("result-disease").textContent =
      isHealthy ? "No disease detected" : data.disease;

    // ── Confidence bar ────────────────────────────────────────────────
    document.getElementById("conf-pct").textContent = data.confidence + "%";
    const fill = document.getElementById("conf-fill");
    fill.className   = "conf-fill " + (isHealthy ? "fill-green" : "fill-red");
    fill.style.width = "0%";
    setTimeout(() => { fill.style.width = data.confidence + "%"; }, 60);

    // ── Cure section ──────────────────────────────────────────────────
    const cureSection = document.getElementById("cure-section");
    if (data.cure && !isHealthy) {
      const c = data.cure;

      document.getElementById("cure-cause").innerHTML = `
        <div class="cure-cause-card">
          <div class="cause-icon">🔬</div>
          <div>
            <div class="cause-label">Root Cause</div>
            <div class="cause-text">${c.cause}</div>
          </div>
        </div>`;

      const steps = c.treatment.map((t, i) => `
        <li>
          <div class="step-num">${i + 1}</div>
          <div class="step-text">${t}</div>
        </li>`).join("");
      document.getElementById("cure-treatment").innerHTML =
        `<ul class="treatment-list">${steps}</ul>`;

      document.getElementById("cure-prevention").innerHTML = `
        <div class="prevention-card">
          <div class="prev-icon">🛡️</div>
          <div>
            <div class="prev-label">Prevention Tips</div>
            <div class="prev-text">${c.prevention}</div>
          </div>
        </div>`;

      showCureTab("cause", document.querySelector(".cure-tab"));
      cureSection.style.display = "block";
    } else {
      cureSection.style.display = "none";
    }

    document.getElementById("result-tip").textContent = isHealthy
      ? "✨ This " + data.plant + " leaf appears healthy. Keep monitoring regularly."
      : "💡 See the tabs above for treatment and prevention steps.";

    resultCard.style.display = "block";
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // ── Cure tab switcher ─────────────────────────────────────────────────
  window.showCureTab = function(tab, btn) {
    // Hide all bodies
    ["cure-cause", "cure-treatment", "cure-prevention"].forEach(id => {
      document.getElementById(id).style.display = "none";
    });
    // Show selected
    document.getElementById("cure-" + tab).style.display = "block";

    // Update tab active state
    document.querySelectorAll(".cure-tab").forEach(t => t.classList.remove("active"));
    if (btn) btn.classList.add("active");
  };

  // Expose to HTML onclick
  window.captureFrame = captureFrame;
  window.retake       = retake;
  window.handleUpload = handleUpload;
  window.analyse      = analyse;
}

// ── Load stats (scan page) ────────────────────────────────────────────────
function loadStats() {
  const totalEl    = document.getElementById("stat-total");
  const healthyEl  = document.getElementById("stat-healthy");
  const diseasedEl = document.getElementById("stat-diseased");
  if (!totalEl) return;

  fetch("/api/stats")
    .then(r => r.json())
    .then(s => {
      totalEl.textContent    = s.total;
      healthyEl.textContent  = s.healthy;
      diseasedEl.textContent = s.diseased;
    })
    .catch(() => {});
}

loadStats();

// ── Helpers ───────────────────────────────────────────────────────────────
function hideResult()       { if (resultCard) resultCard.style.display = "none"; }
function showSpinner(show)  { if (spinner)    spinner.style.display = show ? "flex" : "none"; }
function hideInvalid()      { const c = document.getElementById("invalid-card"); if(c) c.style.display="none"; }
function showInvalid()      { const c = document.getElementById("invalid-card"); if(c) c.style.display="flex"; }

let capturedDataUrl = null;

// Flash animation keyframe (injected once)
const style = document.createElement("style");
style.textContent = `@keyframes flashOut { to { opacity: 0; } }`;
document.head.appendChild(style);
