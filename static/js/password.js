/**
 * PhishGuard - Password Security Analyzer & Generator
 * Zero-storage credential evaluation and client-side reactive UI
 */
document.addEventListener("DOMContentLoaded", () => {
  const passwordInput = document.getElementById("password-input");
  const togglePwdBtn = document.getElementById("btn-toggle-pwd");
  const iconEye = document.getElementById("icon-eye");

  const strengthLabel = document.getElementById("pwd-strength-label");
  const strengthBar = document.getElementById("pwd-strength-bar");
  const valEntropy = document.getElementById("val-entropy");
  const valPool = document.getElementById("val-pool");
  const valLength = document.getElementById("val-length");
  const valCrackTime = document.getElementById("val-crack-time");
  const recommendationsList = document.getElementById("pwd-recommendations");

  const chkLen = document.getElementById("chk-len");
  const chkUpper = document.getElementById("chk-upper");
  const chkLower = document.getElementById("chk-lower");
  const chkDigit = document.getElementById("chk-digit");
  const chkSymbol = document.getElementById("chk-symbol");

  // Generator elements
  const genLength = document.getElementById("gen-length");
  const labelGenLength = document.getElementById("label-gen-length");
  const genUpper = document.getElementById("gen-upper");
  const genNumbers = document.getElementById("gen-numbers");
  const genSymbols = document.getElementById("gen-symbols");
  const btnGenerate = document.getElementById("btn-generate-pwd");
  const generatedPwdText = document.getElementById("generated-pwd-text");
  const btnCopyGen = document.getElementById("btn-copy-gen");
  const copyBtnText = document.getElementById("copy-btn-text");

  let debounceTimer = null;

  // 1. Show/Hide Password Toggle
  togglePwdBtn?.addEventListener("click", () => {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      if (iconEye) iconEye.setAttribute("data-lucide", "eye-off");
    } else {
      passwordInput.type = "password";
      if (iconEye) iconEye.setAttribute("data-lucide", "eye");
    }
    if (window.lucide) lucide.createIcons();
  });

  // 2. Real-time Password Evaluation
  passwordInput?.addEventListener("input", () => {
    const pwd = passwordInput.value;
    updateChecklist(pwd);

    clearTimeout(debounceTimer);
    if (!pwd) {
      resetMetrics();
      return;
    }

    // Debounce backend request slightly for network efficiency
    debounceTimer = setTimeout(() => {
      evaluatePassword(pwd);
    }, 150);
  });

  function updateChecklist(pwd) {
    toggleCriterion(chkLen, pwd.length >= 12);
    toggleCriterion(chkUpper, /[A-Z]/.test(pwd));
    toggleCriterion(chkLower, /[a-z]/.test(pwd));
    toggleCriterion(chkDigit, /[0-9]/.test(pwd));
    toggleCriterion(chkSymbol, /[^A-Za-z0-9]/.test(pwd));
  }

  function toggleCriterion(el, isValid) {
    if (!el) return;
    if (isValid) {
      el.classList.add("valid");
      el.innerHTML = `<i data-lucide="check-circle" class="chk-icon" style="color: var(--neon-green); width: 14px; height: 14px;"></i> <span>${el.querySelector("span").textContent}</span>`;
    } else {
      el.classList.remove("valid");
      el.innerHTML = `<i data-lucide="circle" class="chk-icon" style="color: var(--text-muted); width: 14px; height: 14px;"></i> <span>${el.querySelector("span").textContent}</span>`;
    }
    if (window.lucide) lucide.createIcons();
  }

  async function evaluatePassword(pwd) {
    try {
      const res = await fetch("/api/password/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: pwd })
      });

      if (!res.ok) return;
      const json = await res.json();
      if (json.status !== "success" || !json.data) return;

      const data = json.data;
      renderResults(data);
    } catch (err) {
      console.error("Password analysis error:", err);
    }
  }

  function renderResults(data) {
    // Strength Meter & Label
    const score = data.score; // 0 to 4
    const category = data.category; // Very Weak, Weak, Medium, Strong, Very Strong

    strengthLabel.textContent = category;
    valEntropy.innerHTML = `${data.entropy_bits} <span style="font-size: 0.75rem; color: var(--text-muted);">bits</span>`;
    valPool.innerHTML = `${data.charset_pool_size} <span style="font-size: 0.75rem; color: var(--text-muted);">chars</span>`;
    valLength.textContent = data.length;
    valCrackTime.textContent = data.crack_time_display;

    // Meter colors
    const colors = {
      "Very Weak": "var(--neon-crimson)",
      "Weak": "var(--neon-crimson)",
      "Medium": "var(--neon-gold)",
      "Strong": "var(--neon-cyan)",
      "Very Strong": "var(--neon-green)"
    };
    const widths = ["10%", "25%", "50%", "75%", "100%"];
    const activeColor = colors[category] || "var(--text-muted)";
    const activeWidth = widths[score] || "10%";

    strengthBar.style.width = activeWidth;
    strengthBar.style.backgroundColor = activeColor;
    strengthLabel.style.borderColor = activeColor;
    strengthLabel.style.color = activeColor;

    // Security Directives
    if (data.recommendations && data.recommendations.length > 0) {
      recommendationsList.innerHTML = data.recommendations.map(r => `
        <li class="indicator-item" style="border-left: 3px solid ${activeColor};">
          <i data-lucide="shield-alert" style="width: 14px; height: 14px; color: ${activeColor}; flex-shrink: 0;"></i>
          <span style="font-size: 0.8rem; color: #fff;">${escapeHtml(r)}</span>
        </li>
      `).join("");
    } else {
      recommendationsList.innerHTML = `
        <li class="indicator-item" style="border-left: 3px solid var(--neon-green);">
          <i data-lucide="check-circle" style="width: 14px; height: 14px; color: var(--neon-green); flex-shrink: 0;"></i>
          <span style="font-size: 0.8rem; color: #fff;">Exemplary password complexity. Meets high-assurance threshold.</span>
        </li>
      `;
    }
    if (window.lucide) lucide.createIcons();
  }

  function resetMetrics() {
    strengthLabel.textContent = "Enter Password";
    strengthLabel.className = "badge badge-neutral";
    strengthBar.style.width = "0%";
    valEntropy.innerHTML = `0.0 <span style="font-size: 0.75rem; color: var(--text-muted);">bits</span>`;
    valPool.innerHTML = `0 <span style="font-size: 0.75rem; color: var(--text-muted);">chars</span>`;
    valLength.textContent = "0";
    valCrackTime.textContent = "Instant";
    recommendationsList.innerHTML = `
      <li class="indicator-empty">
        <i data-lucide="info" style="width: 14px; height: 14px;"></i>
        <span>Type or generate a password above to view recommendations.</span>
      </li>
    `;
    updateChecklist("");
    if (window.lucide) lucide.createIcons();
  }

  // 3. Password Generator
  genLength?.addEventListener("input", (e) => {
    labelGenLength.textContent = `${e.target.value} characters`;
  });

  btnGenerate?.addEventListener("click", async () => {
    const length = parseInt(genLength.value, 10);
    const upper = genUpper.checked;
    const digits = genNumbers.checked;
    const symbols = genSymbols.checked;

    try {
      const res = await fetch("/api/password/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          length: length,
          include_uppercase: upper,
          include_digits: digits,
          include_symbols: symbols
        })
      });

      const json = await res.json();
      if (res.ok && json.status === "success") {
        const genPwd = json.data.password;
        generatedPwdText.textContent = genPwd;
        
        // Auto-fill into the input field and trigger analysis!
        passwordInput.value = genPwd;
        updateChecklist(genPwd);
        evaluatePassword(genPwd);
      }
    } catch (err) {
      console.error("Password generation failed:", err);
    }
  });

  btnCopyGen?.addEventListener("click", () => {
    const pwd = generatedPwdText.textContent;
    if (!pwd || pwd === "Click Generate") return;

    navigator.clipboard.writeText(pwd).then(() => {
      copyBtnText.textContent = "Copied!";
      setTimeout(() => {
        copyBtnText.textContent = "Copy";
      }, 2000);
    });
  });

  function escapeHtml(str) {
    return (str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // Initial trigger to generate a default password
  if (btnGenerate) {
    btnGenerate.click();
  }
});
