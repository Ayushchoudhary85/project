/**
 * Interactive Live URL Threat Scanner Engine (Balanced Professional)
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("scanner-form");
  const urlInput = document.getElementById("url-input");
  const btnScan = document.getElementById("btn-scan");
  const progressBox = document.getElementById("scan-progress");
  const progressText = document.getElementById("scan-progress-text");
  const resultCard = document.getElementById("result-card");

  const btnReset = document.getElementById("btn-reset-scan");

  // Reset / Clear workspace button
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      urlInput.value = "";
      if (resultCard) resultCard.style.display = "none";
      if (progressBox) progressBox.style.display = "none";
      urlInput.focus();
    });
  }

  // Preset sample buttons
  document.querySelectorAll(".quick-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      const sampleUrl = pill.getAttribute("data-url");
      urlInput.value = sampleUrl;
      urlInput.focus();
      triggerScan(sampleUrl);
    });
  });

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const rawUrl = urlInput.value.trim();
      if (!rawUrl) {
        showToast("Please enter a valid URL to inspect.", "error");
        return;
      }
      triggerScan(rawUrl);
    });
  }

  async function triggerScan(url) {
    btnScan.disabled = true;
    resultCard.style.display = "none";
    progressBox.style.display = "block";
    
    const steps = [
      "Normalizing URL and parsing domain components...",
      "Computing Shannon entropy on domain and path...",
      "Checking IDN homoglyphs & brand typosquatting...",
      "Running multi-layer RandomForest classification...",
      "Calibrating composite risk score & generating recommendations..."
    ];
    let stepIndex = 0;
    const interval = setInterval(() => {
      stepIndex = (stepIndex + 1) % steps.length;
      progressText.textContent = steps[stepIndex];
    }, 280);

    try {
      const res = await fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      clearInterval(interval);
      progressBox.style.display = "none";
      btnScan.disabled = false;

      const data = await res.json();
      if (!res.ok || data.status !== "success") {
        showToast(data.message || "Failed to analyze URL.", "error");
        return;
      }

      renderResult(data.data);
      updateDashboardStats();
      showToast("URL Threat Analysis Completed.", "success");

    } catch (err) {
      clearInterval(interval);
      progressBox.style.display = "none";
      btnScan.disabled = false;
      showToast("Network error connecting to detection API.", "error");
      console.error(err);
    }
  }

  function renderResult(result) {
    const riskGauge = document.getElementById("result-risk-gauge");
    const predEl = document.getElementById("result-prediction");
    const badgeEl = document.getElementById("result-verdict-badge");
    const urlEl = document.getElementById("result-target-url");
    const confEl = document.getElementById("result-confidence");
    const indCountEl = document.getElementById("indicator-count");
    const indListEl = document.getElementById("result-indicators-list");
    const recListEl = document.getElementById("result-recommendations-list");

    const color = getRiskColor(result.risk_score);
    riskGauge.textContent = result.risk_score;
    riskGauge.style.borderColor = color;
    riskGauge.style.color = color;
    riskGauge.style.boxShadow = `0 0 18px ${color}35`;

    predEl.textContent = result.prediction;
    badgeEl.textContent = `${result.risk_level} Risk`;
    badgeEl.className = `badge ${getVerdictBadgeClass(result.prediction)}`;
    urlEl.textContent = result.url;
    confEl.textContent = `${Math.round(result.confidence * 100)}%`;

    indCountEl.textContent = result.threat_indicators.length;
    indListEl.innerHTML = "";
    if (result.threat_indicators.length === 0) {
      indListEl.innerHTML = `
        <li class="indicator-empty">
          <i data-lucide="check" style="width: 15px; height: 15px;"></i>
          No anomalous behavioral patterns or threat indicators detected.
        </li>
      `;
    } else {
      result.threat_indicators.forEach(ind => {
        const li = document.createElement("li");
        li.className = "indicator-item";
        li.innerHTML = `
          <i data-lucide="alert-triangle" style="width: 15px; height: 15px; flex-shrink: 0; margin-top: 1px;"></i>
          <span>${ind}</span>
        `;
        indListEl.appendChild(li);
      });
    }

    recListEl.innerHTML = "";
    result.recommendations.forEach(rec => {
      const li = document.createElement("li");
      li.style.cssText = "display: flex; gap: 8px; font-size: 0.84rem; color: #cbd5e1; padding: 5px 0;";
      li.innerHTML = `
        <i data-lucide="shield-check" style="width: 15px; height: 15px; color: var(--neon-green); flex-shrink: 0;"></i>
        <span>${rec}</span>
      `;
      recListEl.appendChild(li);
    });

    const feats = result.extracted_features;
    document.getElementById("feat-domain").textContent = result.domain || "-";
    document.getElementById("feat-entropy").textContent = feats.domain_entropy != null ? feats.domain_entropy : "-";
    document.getElementById("feat-scheme").textContent = feats.is_https ? "HTTPS (Encrypted)" : "HTTP (Insecure)";
    document.getElementById("feat-scheme").style.color = feats.is_https ? "var(--neon-green)" : "var(--neon-red)";
    document.getElementById("feat-tld").textContent = feats.is_suspicious_tld ? "Yes (High-Abuse Suffix)" : "Standard";
    document.getElementById("feat-tld").style.color = feats.is_suspicious_tld ? "var(--neon-red)" : "var(--text-primary)";
    document.getElementById("feat-brand").textContent = feats.brand_impersonation_score > 0 ? "Detected Spoofing" : "None";
    document.getElementById("feat-brand").style.color = feats.brand_impersonation_score > 0 ? "var(--neon-red)" : "var(--text-primary)";
    document.getElementById("feat-ip").textContent = feats.has_ip ? "Yes (Raw IP Host)" : "No (Domain)";
    document.getElementById("feat-ip").style.color = feats.has_ip ? "var(--neon-red)" : "var(--text-primary)";
    document.getElementById("feat-subdomains").textContent = feats.num_subdomains;
    document.getElementById("feat-punycode").textContent = feats.has_punycode ? "Detected" : "None";
    document.getElementById("feat-length").textContent = `${feats.url_length} chars`;

    // Populate Domain & URL Characteristics Cards if present
    const cardDomain = document.getElementById("card-domain");
    const cardScheme = document.getElementById("card-scheme");
    const cardEntropy = document.getElementById("card-entropy");
    const cardLength = document.getElementById("card-length");

    if (cardDomain) cardDomain.textContent = result.domain || "-";
    if (cardScheme) {
      cardScheme.textContent = feats.is_https ? "HTTPS (Encrypted)" : "HTTP (Insecure)";
      cardScheme.style.color = feats.is_https ? "var(--neon-green)" : "var(--neon-red)";
    }
    if (cardEntropy) cardEntropy.textContent = `${feats.domain_entropy || 0.0} bits`;
    if (cardLength) cardLength.textContent = `${feats.url_length} chars`;

    resultCard.style.display = "block";
    lucide.createIcons();
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  async function updateDashboardStats() {
    try {
      const res = await fetch("/api/statistics");
      const json = await res.json();
      if (json.status !== "success") return;

      const data = json.data;
      const totalEl = document.getElementById("stat-total");
      const phishEl = document.getElementById("stat-phishing");
      const suspEl = document.getElementById("stat-suspicious");
      const legitEl = document.getElementById("stat-legit");
      const avgEl = document.getElementById("stat-avg");

      if (totalEl) totalEl.textContent = data.total_scans;
      if (phishEl) phishEl.textContent = data.phishing_count;
      if (suspEl) suspEl.textContent = data.suspicious_count;
      if (legitEl) legitEl.textContent = data.legitimate_count;
      if (avgEl) avgEl.textContent = data.average_risk_score;

      const tbody = document.getElementById("recent-scans-tbody");
      if (tbody && data.recent_scans && data.recent_scans.length > 0) {
        tbody.innerHTML = data.recent_scans.map(scan => `
          <tr>
            <td class="url-cell" title="${scan.url}">${scan.url}</td>
            <td><code>${scan.domain}</code></td>
            <td>
              <span class="badge ${getVerdictBadgeClass(scan.prediction)}">
                ${scan.prediction.replace("Potential ", "").replace("Likely ", "")}
              </span>
            </td>
            <td>
              <strong style="font-family: var(--font-mono); color: ${getRiskColor(scan.risk_score)}">
                ${scan.risk_score} / 100
              </strong>
            </td>
            <td style="color: var(--text-muted); font-size: 0.78rem; font-family: var(--font-mono);">
              ${scan.scan_timestamp.slice(0, 19).replace("T", " ")}
            </td>
          </tr>
        `).join("");
      }
    } catch (e) {
      console.error("Failed to refresh stats:", e);
    }
  }

  // Initial load of recent scan history
  updateDashboardStats();
});
