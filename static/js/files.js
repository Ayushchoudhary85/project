/**
 * PhishGuard - File Virus & Threat Scanner
 * Drag-and-drop multipart upload, byte verification, and telemetry history
 */
document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const uploadForm = document.getElementById("file-upload-form");
  const uploadPreview = document.getElementById("upload-preview");
  const selectedFilename = document.getElementById("selected-filename");
  const selectedFilesize = document.getElementById("selected-filesize");
  const btnCancelFile = document.getElementById("btn-cancel-file");
  const btnSubmitScan = document.getElementById("btn-submit-scan");
  const progressContainer = document.getElementById("scan-progress-container");
  const progressBar = document.getElementById("scan-progress-bar");
  const progressPct = document.getElementById("scan-progress-pct");
  const statusText = document.getElementById("scan-status-text");

  const fileScansTbody = document.getElementById("file-scans-tbody");
  const btnRefreshFiles = document.getElementById("btn-refresh-files");
  const btnClearFiles = document.getElementById("btn-clear-file-scans");
  const btnToggleSetup = document.getElementById("btn-toggle-setup-help");
  const setupDrawer = document.getElementById("setup-help-drawer");
  const fileErrorAlert = document.getElementById("file-error-alert");
  const fileErrorMsg = document.getElementById("file-error-msg");

  let activeFile = null;

  // Toggle ClamAV installation guidance if present
  if (btnToggleSetup && setupDrawer) {
    btnToggleSetup.addEventListener("click", () => {
      const isClosed = setupDrawer.style.display === "none" || !setupDrawer.style.display;
      setupDrawer.style.display = isClosed ? "block" : "none";
      btnToggleSetup.innerHTML = isClosed ? "Hide Guidance &uarr;" : "Install ClamAV &darr;";
    });
  }

  function showError(msg) {
    if (fileErrorAlert && fileErrorMsg) {
      fileErrorMsg.textContent = msg;
      fileErrorAlert.style.display = "flex";
      if (window.lucide) lucide.createIcons();
    } else {
      alert(msg);
    }
  }

  function hideError() {
    if (fileErrorAlert) {
      fileErrorAlert.style.display = "none";
    }
  }

  // 1. Drag and Drop Handlers
  if (dropZone && fileInput) {
    dropZone.addEventListener("click", () => fileInput.click());

    ["dragenter", "dragover"].forEach(evt => {
      dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach(evt => {
      dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("dragover");
      });
    });

    dropZone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length > 0) {
        handleFileSelection(dt.files[0]);
      }
    });

    fileInput.addEventListener("change", (e) => {
      if (fileInput.files && fileInput.files.length > 0) {
        handleFileSelection(fileInput.files[0]);
      }
    });
  }

  function handleFileSelection(file) {
    if (!file) return;
    hideError();

    const maxMb = parseInt(dropZone?.dataset?.maxSizeMb, 10) || 32;
    const maxBytes = maxMb * 1024 * 1024;

    if (file.size > maxBytes) {
      showError(`File size (${formatBytes(file.size)}) exceeds maximum limit of ${maxMb} MB. Please select a smaller file.`);
      fileInput.value = "";
      return;
    }

    if (file.size === 0) {
      showError("Selected file is empty (0 bytes). Please select a valid file.");
      fileInput.value = "";
      return;
    }

    activeFile = file;
    selectedFilename.textContent = file.name;
    selectedFilesize.textContent = formatBytes(file.size);
    uploadPreview.style.display = "block";
    btnSubmitScan.disabled = false;
    dropZone.style.display = "none";
    if (window.lucide) lucide.createIcons();
  }

  btnCancelFile?.addEventListener("click", () => {
    resetSelection();
  });

  function resetSelection() {
    activeFile = null;
    fileInput.value = "";
    uploadPreview.style.display = "none";
    progressContainer.style.display = "none";
    dropZone.style.display = "block";
    btnSubmitScan.disabled = true;
    hideError();
  }

  // 2. Upload and Scan
  uploadForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!activeFile) return;

    btnSubmitScan.disabled = true;
    progressContainer.style.display = "block";
    progressBar.style.width = "25%";
    progressPct.textContent = "25%";
    statusText.textContent = "Uploading payload to volatile buffer...";

    const formData = new FormData();
    formData.append("file", activeFile);

    try {
      setTimeout(() => {
        progressBar.style.width = "65%";
        progressPct.textContent = "65%";
        statusText.textContent = "Extracting magic byte signatures & computing hashes...";
      }, 300);

      const res = await fetch("/api/file/scan", {
        method: "POST",
        body: formData
      });

      progressBar.style.width = "95%";
      progressPct.textContent = "95%";
      statusText.textContent = "Verifying threat indicators & finalizing verdict...";

      const data = await res.json();
      if (res.ok && data.status === "success") {
        progressBar.style.width = "100%";
        progressPct.textContent = "100%";
        statusText.textContent = "Analysis complete! Redirecting...";

        setTimeout(() => {
          window.location.href = `/file-scanner/${data.data.id}`;
        }, 400);
      } else {
        alert("File scan failed: " + (data.message || "Unknown error"));
        resetSelection();
      }
    } catch (err) {
      alert("Network transmission error: " + err.message);
      resetSelection();
    }
  });

  // 3. Recent Scans Table
  async function loadRecentFileScans() {
    if (!fileScansTbody) return;
    try {
      const res = await fetch("/api/file/history?limit=10");
      const data = await res.json();

      if (!res.ok || data.status !== "success") {
        fileScansTbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--neon-crimson); padding: 24px;">Failed to load logs.</td></tr>`;
        return;
      }

      if (data.scans.length === 0) {
        fileScansTbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 30px; font-family: var(--font-mono);">No file analyses recorded yet.</td></tr>`;
        return;
      }

      fileScansTbody.innerHTML = data.scans.map(s => `
        <tr>
          <td style="font-family: var(--font-mono); color: var(--text-muted);">#${s.id}</td>
          <td style="font-weight: 600; color: #fff;">${escapeHtml(s.filename)}</td>
          <td style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-muted);" title="${s.sha256}">
            ${s.sha256.substring(0, 16)}...
          </td>
          <td style="font-family: var(--font-mono); font-size: 0.8rem;">${formatBytes(s.size_bytes)}</td>
          <td style="font-family: var(--font-mono); font-size: 0.74rem; color: var(--neon-cyan);">${escapeHtml(s.mime_type)}</td>
          <td><span class="badge ${getStatusBadge(s.status)}">${s.status}</span></td>
          <td style="font-size: 0.76rem; color: var(--text-muted); font-family: var(--font-mono);">${s.timestamp}</td>
          <td style="text-align: right;">
            <a href="/file-scanner/${s.id}" class="btn-secondary" style="padding: 4px 8px; font-size: 0.72rem; text-decoration: none;">View</a>
            <a href="/api/file/report/${s.id}" class="btn-secondary" style="padding: 4px 8px; font-size: 0.72rem; text-decoration: none;">PDF</a>
            <button onclick="deleteFileRecord(${s.id})" class="btn-danger" style="padding: 4px 8px; font-size: 0.72rem;">Delete</button>
          </td>
        </tr>
      `).join("");
      if (window.lucide) lucide.createIcons();
    } catch (err) {
      fileScansTbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--neon-crimson); padding: 24px;">Error: ${err.message}</td></tr>`;
    }
  }

  function getStatusBadge(status) {
    if (status === "Clean") return "badge-legitimate";
    if (status === "Malicious") return "badge-phishing";
    if (status === "Suspicious") return "badge-suspicious";
    return "badge-neutral";
  }

  function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  function escapeHtml(str) {
    return (str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  window.deleteFileRecord = async (id) => {
    if (!confirm(`Delete file scan #${id}?`)) return;
    try {
      const res = await fetch(`/api/file/history/${id}`, { method: "DELETE" });
      if (res.ok) loadRecentFileScans();
    } catch (e) {
      alert("Delete failed: " + e.message);
    }
  };

  btnRefreshFiles?.addEventListener("click", loadRecentFileScans);
  btnClearFiles?.addEventListener("click", async () => {
    if (!confirm("Clear all file scan history?")) return;
    try {
      const res = await fetch("/api/file/history/clear", { method: "POST" });
      if (res.ok) loadRecentFileScans();
    } catch (e) {
      alert("Clear failed: " + e.message);
    }
  });

  loadRecentFileScans();
});
