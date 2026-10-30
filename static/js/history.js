/**
 * Audit History Management & Inspection Engine (Balanced Professional)
 */

document.addEventListener("DOMContentLoaded", () => {
  let currentOffset = 0;
  const limit = 15;
  let totalRecords = 0;

  const tbody = document.getElementById("history-tbody");
  const searchInput = document.getElementById("filter-search");
  const predSelect = document.getElementById("filter-prediction");
  const riskSelect = document.getElementById("filter-risk");
  const btnPrev = document.getElementById("btn-prev-page");
  const btnNext = document.getElementById("btn-next-page");
  const paginationInfo = document.getElementById("pagination-info");
  const btnRefresh = document.getElementById("btn-refresh");
  const btnClearHistory = document.getElementById("btn-clear-history");

  const modal = document.getElementById("scan-modal");
  const modalBody = document.getElementById("modal-body");
  const btnCloseModal = document.getElementById("btn-close-modal");

  loadHistory();

  let searchTimeout = null;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentOffset = 0;
      loadHistory();
    }, 280);
  });

  predSelect.addEventListener("change", () => {
    currentOffset = 0;
    loadHistory();
  });

  riskSelect.addEventListener("change", () => {
    currentOffset = 0;
    loadHistory();
  });

  btnRefresh.addEventListener("click", () => {
    loadHistory();
    showToast("Audit logs refreshed.", "info");
  });

  btnPrev.addEventListener("click", () => {
    if (currentOffset >= limit) {
      currentOffset -= limit;
      loadHistory();
    }
  });

  btnNext.addEventListener("click", () => {
    if (currentOffset + limit < totalRecords) {
      currentOffset += limit;
      loadHistory();
    }
  });

  btnClearHistory.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to clear all audit records? This action cannot be undone.")) return;

    try {
      const res = await fetch("/api/history/clear", { method: "POST" });
      const json = await res.json();
      if (res.ok) {
        showToast(json.message || "History cleared.", "success");
        currentOffset = 0;
        loadHistory();
      } else {
        showToast(json.message || "Failed to clear history.", "error");
      }
    } catch (e) {
      showToast("Network error while clearing logs.", "error");
    }
  });

  btnCloseModal.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  async function loadHistory() {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 32px; font-family: var(--font-mono);">
          Querying audit database...
        </td>
      </tr>
    `;

    const search = encodeURIComponent(searchInput.value.trim());
    const pred = encodeURIComponent(predSelect.value);
    const risk = encodeURIComponent(riskSelect.value);

    try {
      const res = await fetch(
        `/api/history?limit=${limit}&offset=${currentOffset}&search=${search}&prediction=${pred}&risk_level=${risk}`
      );
      const json = await res.json();

      if (!res.ok || json.status !== "success") {
        tbody.innerHTML = `
          <tr>
            <td colspan="8" style="text-align: center; color: var(--neon-red); padding: 30px;">
              ${json.message || "Database query failed."}
            </td>
          </tr>
        `;
        return;
      }

      totalRecords = json.total;
      renderTable(json.scans);
      updatePagination(json.total, json.offset, json.limit);

    } catch (err) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; color: var(--neon-red); padding: 30px;">
            Connection error fetching audit logs.
          </td>
        </tr>
      `;
    }
  }

  function renderTable(scans) {
    if (!scans || scans.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 36px; font-family: var(--font-mono);">
            No records match the current filter criteria.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = scans.map(scan => {
      const riskColor = getRiskColor(scan.risk_score);
      const badgeClass = getVerdictBadgeClass(scan.prediction);
      const dateStr = scan.scan_timestamp ? scan.scan_timestamp.slice(0, 19).replace("T", " ") : "-";

      return `
        <tr>
          <td><span style="font-family: var(--font-mono); color: var(--text-muted);">#${scan.id}</span></td>
          <td class="url-cell" title="${scan.url}">${scan.url}</td>
          <td><code>${scan.domain}</code></td>
          <td><span class="badge ${badgeClass}">${scan.prediction}</span></td>
          <td><strong style="color: ${riskColor}; font-family: var(--font-mono);">${scan.risk_score}</strong></td>
          <td><span style="color: var(--neon-green); font-family: var(--font-mono); font-weight: 600;">${Math.round(scan.confidence * 100)}%</span></td>
          <td style="color: var(--text-muted); font-size: 0.78rem; font-family: var(--font-mono);">${dateStr}</td>
          <td style="text-align: right;">
            <div style="display: flex; justify-content: flex-end; gap: 6px;">
              <button class="btn-secondary" style="padding: 4px 8px;" onclick="inspectScan(${scan.id})" title="Inspect Dossier">
                <i data-lucide="eye" style="width: 14px; height: 14px;"></i>
              </button>
              <button class="btn-icon-danger" onclick="deleteSingleScan(${scan.id})" title="Delete Record">
                <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

    lucide.createIcons();
  }

  function updatePagination(total, offset, pageLimit) {
    const start = total === 0 ? 0 : offset + 1;
    const end = Math.min(offset + pageLimit, total);
    paginationInfo.textContent = `Showing ${start}-${end} of ${total} records`;

    btnPrev.disabled = offset === 0;
    btnNext.disabled = offset + pageLimit >= total;
  }

  window.inspectScan = async function(scanId) {
    try {
      const res = await fetch(`/api/history/${scanId}`);
      const json = await res.json();
      if (!res.ok || json.status !== "success") {
        showToast("Error retrieving scan details.", "error");
        return;
      }

      const scan = json.data;
      const feats = scan.extracted_features || {};
      const indicators = scan.threat_indicators || [];

      modalBody.innerHTML = `
        <div style="background: #090a0d; padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
          <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-family: var(--font-mono);">Inspected Target</div>
          <div style="word-break: break-all; font-family: var(--font-mono); font-size: 0.86rem; color: #fff; margin-top: 4px;">${scan.url}</div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
          <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">Verdict Classification</div>
            <div style="margin-top: 6px;"><span class="badge ${getVerdictBadgeClass(scan.prediction)}">${scan.prediction}</span></div>
          </div>
          <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">Risk Index & Level</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: ${getRiskColor(scan.risk_score)}; font-family: var(--font-mono); margin-top: 2px;">
              ${scan.risk_score} / 100 (${scan.risk_level})
            </div>
          </div>
        </div>

        <div>
          <h4 style="font-size: 0.86rem; margin-bottom: 8px; color: #fff;">Detected Threat Indicators (${indicators.length})</h4>
          ${
            indicators.length === 0 
              ? '<p style="color: var(--neon-green); font-size: 0.84rem; font-family: var(--font-mono);">No anomalous indicators recorded.</p>'
              : `<ul class="indicator-list">${indicators.map(i => `<li class="indicator-item">${i}</li>`).join("")}</ul>`
          }
        </div>

        <div>
          <h4 style="font-size: 0.86rem; margin-bottom: 8px; color: #fff;">Extracted Feature Telemetry</h4>
          <table class="feature-table">
            <tr><td>Domain Shannon Entropy</td><td>${feats.domain_entropy != null ? feats.domain_entropy : "-"}</td></tr>
            <tr><td>Total URL Entropy</td><td>${feats.url_entropy != null ? feats.url_entropy : "-"}</td></tr>
            <tr><td>URL Length</td><td>${feats.url_length || "-"} characters</td></tr>
            <tr><td>Subdomain Depth</td><td>${feats.num_subdomains || 0}</td></tr>
            <tr><td>Raw IP Indicator</td><td>${feats.has_ip ? "Yes (Raw IP Host)" : "No (Domain)"}</td></tr>
            <tr><td>Suspicious TLD</td><td>${feats.is_suspicious_tld ? "Yes" : "No"}</td></tr>
            <tr><td>Brand Impersonation Score</td><td>${feats.brand_impersonation_score || 0}</td></tr>
          </table>
        </div>
      `;

      modal.style.display = "flex";
      lucide.createIcons();

    } catch (e) {
      showToast("Error loading scan details.", "error");
    }
  };

  window.deleteSingleScan = async function(scanId) {
    if (!confirm(`Delete audit record #${scanId}?`)) return;

    try {
      const res = await fetch(`/api/history/${scanId}`, { method: "DELETE" });
      const json = await res.json();
      if (res.ok) {
        showToast("Record deleted.", "success");
        loadHistory();
      } else {
        showToast(json.message || "Delete failed.", "error");
      }
    } catch (e) {
      showToast("Network error while deleting record.", "error");
    }
  };
});
