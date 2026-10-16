/* Aplica o tema salvo antes de pintar a página (evita piscar). Arquivo separado porque a CSP não permite script inline. */
try { var theme = localStorage.getItem("kstudy-admin-theme"); if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme; } catch (e) { /* sem armazenamento */ }
