/**
 * Threat Analytics & Visual Telemetry Engine (Chart.js - Neon Theme)
 */

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("/api/analytics");
    const json = await res.json();
    if (!res.ok || json.status !== "success") return;

    const data = json.data;
    const stats = data.statistics;

    initVerdictChart(stats.prediction_distribution);
    initRiskChart(stats.risk_distribution);
    initIndicatorsChart(data.top_threat_indicators);

  } catch (err) {
    console.error("Error loading analytics data:", err);
  }

  function initVerdictChart(verdicts) {
    const ctx = document.getElementById("chart-verdicts");
    if (!ctx) return;

    const labels = ["Likely Legitimate", "Suspicious", "Potential Phishing"];
    const values = [
      verdicts["Likely Legitimate"] || 0,
      verdicts["Suspicious"] || 0,
      verdicts["Potential Phishing"] || 0
    ];

    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: ["#00e599", "#ffb703", "#ff3b30"],
          borderColor: "#0e1014",
          borderWidth: 4,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#9aa0a6", font: { family: "GeistMono, monospace", size: 11 } }
          }
        },
        cutout: "70%"
      }
    });
  }

  function initRiskChart(riskCounts) {
    const ctx = document.getElementById("chart-risk");
    if (!ctx) return;

    const labels = ["Low (0-29)", "Medium (30-59)", "High (60-79)", "Critical (80-100)"];
    const values = [
      riskCounts["Low"] || 0,
      riskCounts["Medium"] || 0,
      riskCounts["High"] || 0,
      riskCounts["Critical"] || 0
    ];

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Entities",
          data: values,
          backgroundColor: ["#00e599", "#ffb703", "#ff6b6b", "#ff3b30"],
          borderRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            ticks: { color: "#9aa0a6", font: { family: "GeistMono, monospace", size: 10 } },
            grid: { display: false }
          },
          y: {
            ticks: { color: "#9aa0a6", font: { family: "GeistMono, monospace", size: 10 }, stepSize: 1 },
            grid: { color: "rgba(255, 255, 255, 0.05)" }
          }
        }
      }
    });
  }

  function initIndicatorsChart(indicators) {
    const ctx = document.getElementById("chart-indicators");
    if (!ctx) return;

    if (!indicators || indicators.length === 0) {
      indicators = [
        { indicator: "Insecure plain HTTP protocol", count: 0 },
        { indicator: "Suspected brand impersonation", count: 0 },
        { indicator: "Domain registered under high-abuse TLD", count: 0 },
        { indicator: "High domain entropy (DGA)", count: 0 }
      ];
    }

    const labels = indicators.map(i => i.indicator);
    const values = indicators.map(i => i.count);

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Occurrences",
          data: values,
          backgroundColor: "rgba(0, 229, 153, 0.75)",
          borderColor: "#00e599",
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            ticks: { color: "#9aa0a6", font: { family: "GeistMono, monospace", size: 10 }, stepSize: 1 },
            grid: { color: "rgba(255, 255, 255, 0.05)" }
          },
          y: {
            ticks: { color: "#ededed", font: { size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }
});
