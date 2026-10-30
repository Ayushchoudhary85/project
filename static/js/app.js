/**
 * Global Utility Functions for PhishGuard (Neon Theme)
 */

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  
  const icon = type === "error" ? "🛑" : type === "success" ? "✅" : "⚡";
  toast.innerHTML = `<span style="margin-right: 8px;">${icon}</span><span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = "opacity 0.3s ease, transform 0.3s ease";
    toast.style.opacity = "0";
    toast.style.transform = "translateX(40px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function getVerdictBadgeClass(prediction) {
  if (prediction === "Potential Phishing") return "badge-phishing";
  if (prediction === "Suspicious") return "badge-suspicious";
  return "badge-legitimate";
}

function getRiskColor(score) {
  if (score >= 80) return "#ff3b30"; // Neon Red
  if (score >= 60) return "#ff6b6b"; // Neon Coral
  if (score >= 30) return "#ffb703"; // Neon Amber
  return "#00e599"; // Neon Green
}
