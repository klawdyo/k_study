"use strict";
/* Interface do aluno. Não guarda estado próprio: conteúdo e progresso vêm da API e voltam para ela.
   Identificadores em inglês; textos mostrados ao aluno em português. Rotas por hash:
     #/                          grade de trilhas
     #/t/<slug>                  trilha (abre o próximo item pendente)
     #/t/<slug>/<bloco>          bloco
     #/t/<slug>/<bloco>/<item>   aula */

const $ = (selector, root = document) => root.querySelector(selector);
const h = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (value !== false && value != null) node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) if (child != null && child !== false) node.append(child.nodeType ? child : document.createTextNode(String(child)));
  return node;
};

const KINDS = {
  video:     { icon: "smart_display", label: "Vídeo" },
  markdown:  { icon: "article", label: "Leitura" },
  pdf:       { icon: "picture_as_pdf", label: "PDF" },
  link:      { icon: "link", label: "Matéria" },
  questions: { icon: "quiz", label: "Questões" },
};

/* Ícones: Material Design (outlined), servidos de vendor/icons */
const ICON_NAMES = ["smart_display", "article", "picture_as_pdf", "link", "quiz", "check_circle_filled", "radio_button_unchecked", "menu", "open_in_new"];
const SVG = {};
async function loadIcons() {
  await Promise.all(ICON_NAMES.map(async (name) => { try { SVG[name] = await getText(`vendor/icons/${name}.svg`); } catch { SVG[name] = ""; } }));
}
const icon = (name, cls = "") => h("span", { class: "ic " + cls, "aria-hidden": "true", html: SVG[name] || "" });

const state = {
  user: null,                                       // {email, name, isAdmin} ou null
  csrf: null,                                       // token CSRF da sessão (vem de /api/auth/me)
  oauth: { google: false },                         // provedores configurados no servidor (só então o botão aparece)
  oauthError: null,                                 // mensagem fixa depois de uma entrada com o Google que falhou
  trails: null,                                     // lista de /api/trails
  slug: null, trail: null,                          // trilha aberta (manifesto)
  blocks: [],                                       // [{entry, url, data, error}] de todos os blocos da trilha
  block: null, blockUrl: null, items: [],           // bloco aberto; itens achatados (cada um com .section e .key)
  progress: { items: {}, answers: {}, notes: {} },  // espelho do que a API devolveu
  current: null,
};

/* ---------- API ---------- */
class ApiError extends Error {
  constructor(status, code, message) { super(message); this.status = status; this.code = code; }
}
async function api(method, url, body, retried = false) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (method !== "GET" && state.csrf) headers["X-CSRF-Token"] = state.csrf;
  let response;
  try {
    response = await fetch(url, { method, cache: "no-store", headers, body: body !== undefined ? JSON.stringify(body) : undefined });
  } catch {
    throw new ApiError(0, "network", "Não consegui falar com o servidor. Confira se ele está rodando e se a rede está funcionando.");
  }
  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = null; }
  if (!response.ok) {
    if (response.status === 403 && data?.error === "csrf_failed" && !retried) {      // token vencido: pega outro e tenta uma vez
      await loadSession();
      return api(method, url, body, true);
    }
    if (response.status === 401 && state.user) { onLoggedOut(); }
    const error = new ApiError(response.status, data?.error || "http", data?.message || `O servidor respondeu com erro ${response.status}.`);
    error.retryAfter = Number(response.headers.get("Retry-After")) || 0;
    throw error;
  }
  return data;
}
/* Lê quem está logado e o token CSRF (também antes do login, para as telas de entrada). */
async function loadSession() {
  const me = await api("GET", "/api/auth/me");
  state.user = me?.student || null;
  state.csrf = me?.csrfToken || null;
  state.oauth = { google: !!me?.oauth?.google };
  return me;
}
async function getText(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`erro ${response.status} ao carregar ${url}`);
  return response.text();
}
const getJson = (url) => api("GET", url);

const trailBase = () => `/api/trails/${encodeURIComponent(state.slug)}`;
/* Conteúdo SEMPRE por ids (o servidor traduz para arquivo); nunca por caminho. */
const blockUrl = (blockId) => `${trailBase()}/blocks/${encodeURIComponent(blockId)}`;
const itemUrl = (blockId, itemId, part) => `${blockUrl(blockId)}/items/${encodeURIComponent(itemId)}/${part}`;
const keyPath = (key) => key.split("/").map(encodeURIComponent).join("/");
const trailHash = (slug, block, item) => "#/t/" + [slug, block, item].filter(Boolean).map(encodeURIComponent).join("/");

/* Toda mudança de progresso passa por aqui; a API grava e devolve o estado completo. */
async function mutate(method, path, body) {
  try {
    state.progress = normalizeProgress(await api(method, `${trailBase()}/progress/${path}`, body));
    banner(null);
  } catch (error) {
    if (error.status === 401) return;
    banner("Não consegui gravar seu progresso (" + error.message + ") Nada foi salvo.");
    await reloadProgress();
  }
}
const normalizeProgress = (p) => ({ items: p?.items || {}, answers: p?.answers || {}, notes: p?.notes || {} });
async function reloadProgress() {
  try { state.progress = normalizeProgress(await getJson(`${trailBase()}/progress`)); banner(null); return true; }
  catch (error) { if (error.status !== 401) banner("O servidor não respondeu: " + error.message); return false; }
}
function banner(message) {
  let node = $("#banner");
  if (!message) { if (node) node.remove(); return; }
  if (!node) { node = h("div", { id: "banner", class: "banner", role: "alert" }); document.body.prepend(node); }
  node.textContent = message;
}

/* Ao voltar para a aba, relê o estado na API (a única fonte da verdade). */
let syncing = false;
async function sync() {
  if (!state.user || !state.block || syncing) return;
  syncing = true;
  const before = JSON.stringify(state.progress);
  if (await reloadProgress() && JSON.stringify(state.progress) !== before) {
    drawMenu();
    const typing = document.activeElement && document.activeElement.tagName === "TEXTAREA";
    if (state.current && !typing) showItem(state.current, { mark: false, track: false });
  }
  syncing = false;
}
document.addEventListener("visibilitychange", () => { if (!document.hidden) sync(); });
window.addEventListener("focus", sync);

const csrfHeaders = () => ({ "Content-Type": "application/json", "X-CSRF-Token": state.csrf || "" });

/* ---------- rastreio de tempo ---------- */
/* Contrato (seção 6): open cria a visita; a cada 10 s com a aba visível e em foco vai um beat de 10 s;
   ao sair, leave com o resto. Falhas aqui são ignoradas: nunca podem quebrar a interface. */
const tracker = {
  rec: null,                                         // {visit, secs}: visita atual
  timer: null,
  start(trail, block, item) {
    this.stop();
    const rec = { visit: null, secs: 0 };
    this.rec = rec;
    try {
      fetch("/api/track", { method: "POST", headers: csrfHeaders(), cache: "no-store",
        body: JSON.stringify({ event: "open", trail, block, item }) })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => { if (d && d.visit != null) rec.visit = d.visit; })
        .catch(() => {});
      this.timer = setInterval(() => this.tick(), 1000);
    } catch { /* ignorado */ }
  },
  tick() {
    const rec = this.rec;
    if (!rec || document.visibilityState !== "visible" || !document.hasFocus()) return;
    rec.secs++;
    if (rec.secs >= 10 && rec.visit != null) {
      rec.secs -= 10;
      try {
        fetch("/api/track", { method: "POST", headers: csrfHeaders(), cache: "no-store", keepalive: true,
          body: JSON.stringify({ event: "beat", visit: rec.visit, seconds: 10 }) }).catch(() => {});
      } catch { /* ignorado */ }
    }
  },
  /* envia o resto (sem encerrar a visita); usado ao esconder a aba e ao fechar a página */
  flush() {
    const rec = this.rec;
    if (!rec || rec.visit == null || rec.secs < 1) return;
    const seconds = Math.min(rec.secs, 30);
    rec.secs = 0;
    try {
      // sendBeacon não envia cabeçalhos: o token CSRF vai no corpo (campo csrf)
      const body = new Blob([JSON.stringify({ event: "leave", visit: rec.visit, seconds, csrf: state.csrf })], { type: "application/json" });
      if (!(navigator.sendBeacon && navigator.sendBeacon("/api/track", body))) {
        fetch("/api/track", { method: "POST", headers: csrfHeaders(), keepalive: true, body: body }).catch(() => {});
      }
    } catch { /* ignorado */ }
  },
  stop() {
    this.flush();
    clearInterval(this.timer); this.timer = null; this.rec = null;
  },
};
window.addEventListener("pagehide", () => tracker.flush());
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") tracker.flush(); });

/* ---------- navegação (hash) ---------- */
function parseRoute() {
  const parts = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean).map((p) => { try { return decodeURIComponent(p); } catch { return p; } });
  if (parts[0] === "t" && parts[1]) return { view: "trail", slug: parts[1], block: parts[2], item: parts[3] };
  return { view: "home" };
}
function setView(view) {
  document.body.className = "view-" + view;
  document.body.classList.remove("menu-open");
  $("#menu-btn").setAttribute("aria-expanded", "false");
}
let routeToken = 0, markOnNext = false;

async function renderRoute() {
  const token = ++routeToken;
  const route = parseRoute();
  if (!state.user) { tracker.stop(); setView("login"); renderLogin(); return; }
  try {
    if (route.view === "home") { tracker.stop(); await renderHome(token); }
    else await renderTrailRoute(route, token);
  } catch (error) {
    if (token !== routeToken) return;
    if (error.status === 401) return;
    $("#main").replaceChildren(h("div", { class: "verdict no", role: "alert" }, "Não consegui abrir esta página: " + error.message),
      h("p", {}, h("a", { class: "btn", href: "#/" }, "← Voltar às trilhas")));
  }
}
window.addEventListener("hashchange", renderRoute);

async function onLoggedOut() {
  state.user = null; state.trails = null; state.slug = null; state.trail = null; state.block = null; state.current = null;
  tracker.stop(); banner(null);
  try { await loadSession(); } catch { /* a tela de entrada mostra o erro ao enviar */ }
  renderRoute();
}

/* ---------- topo ---------- */
function drawUser() {
  const user = state.user;
  const name = user?.name || "", email = user?.email || "";
  $("#user-name").textContent = name;
  $("#user-email").textContent = email;
  $("#user-box").title = email ? `Você está identificado como ${name ? name + " — " : ""}${email}` : "";
}
$("#logout-btn").addEventListener("click", async () => {
  tracker.stop();
  try { await api("POST", "/api/auth/logout", {}); } catch { /* sai da tela mesmo se falhar */ }
  state.user = null;
  location.hash = "#/";
  onLoggedOut();
});

/* ---------- entrada em etapas: e-mail -> senha (conta existe) ou cadastro (conta nova) ---------- */
const EMAIL_RE = /^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$/;
function waitMessage(error) {
  if (error.status !== 429) return error.message;
  const minutes = Math.max(1, Math.ceil((error.retryAfter || 60) / 60));
  return `Muitas tentativas. Tente de novo em ${minutes} ${minutes === 1 ? "minuto" : "minutos"}.`;
}
function passwordField(id, label, autocomplete) {
  const input = h("input", { id, class: "text-input", type: "password", name: id, autocomplete, required: true, maxlength: "128" });
  const toggle = h("button", { type: "button", class: "btn small-btn show-pass", "aria-pressed": "false",
    onclick: () => { const shown = input.type === "text"; input.type = shown ? "password" : "text"; toggle.setAttribute("aria-pressed", String(!shown)); toggle.textContent = shown ? "Mostrar" : "Ocultar"; } }, "Mostrar");
  return { input, node: h("div", {}, h("label", { for: id, class: "field-label" }, label), h("div", { class: "pass-row" }, input, toggle)) };
}

/* O botão só existe quando o servidor informa (em /api/auth/me) que o Google está configurado. É um link: a
   navegação vai para o servidor, que redireciona ao Google (o retorno é fixo: /auth/oauth/google/callback). */
const googleButton = () => h("a", { class: "btn google-btn", href: "/auth/oauth/google/start" },
  h("span", { class: "g-mark", "aria-hidden": "true" }, "G"), "Entrar com o Google");
const OAUTH_MESSAGES = {
  denied: "Você cancelou a entrada com o Google.",
  invalid_state: "A entrada com o Google expirou ou foi interrompida. Tente de novo.",
  failed: "Não foi possível entrar com o Google. Tente de novo ou use e-mail e senha.",
  unverified: "O Google informa que o e-mail dessa conta não foi verificado.",
  too_many: "Muitas tentativas. Aguarde alguns minutos e tente de novo.",
};

function renderLogin(step = { name: "email" }) {
  document.title = "Entrar · k_study";
  $("#sidebar").replaceChildren();
  const error = h("p", { id: "login-error", class: "form-error", role: "alert" });
  const fail = (e) => { error.textContent = waitMessage(e); };
  const change = (email) => h("button", { type: "button", class: "link-btn", onclick: () => renderLogin({ name: "email", email }) }, "(trocar)");
  let card;

  if (step.name === "email") {
    const email = h("input", { id: "email-input", class: "text-input", type: "email", name: "username", autocomplete: "username", inputmode: "email",
      required: true, placeholder: "voce@exemplo.com", spellcheck: "false", value: step.email || "", "aria-describedby": "login-help login-error" });
    const submit = h("button", { class: "btn primary", type: "submit" }, "Continuar");
    card = h("form", { class: "login-card", novalidate: true },
      h("h1", { class: "page-title" }, "Bem-vindo ao k_study"),
      h("p", { id: "login-help" }, "Informe seu e-mail para entrar ou criar sua conta. Seu progresso fica guardado nela."),
      state.oauthError ? h("p", { class: "form-error", role: "alert" }, state.oauthError) : null,
      state.oauth.google ? [googleButton(), h("p", { class: "or-line" }, h("span", {}, "ou entre com e-mail e senha"))] : null,
      h("label", { for: "email-input", class: "field-label" }, "Seu e-mail"), email, error,
      h("div", { class: "login-actions" }, submit));
    card.addEventListener("submit", async (event) => {
      event.preventDefault();
      const value = email.value.trim().toLowerCase();
      error.textContent = "";
      if (!EMAIL_RE.test(value)) { error.textContent = "Digite um e-mail válido, como voce@exemplo.com."; email.focus(); return; }
      submit.disabled = true; submit.textContent = "Verificando…";
      try {
        const result = await api("POST", "/api/auth/check", { email: value });
        renderLogin({ name: result.exists && !result.needsSetup ? "password" : "register", email: value, firstUser: result.firstUser, setup: result.needsSetup });
      } catch (e) { fail(e); submit.disabled = false; submit.textContent = "Continuar"; email.focus(); }
    });
  } else if (step.name === "password") {
    const pass = passwordField("password-input", "Sua senha", "current-password");
    const submit = h("button", { class: "btn primary", type: "submit" }, "Entrar");
    card = h("form", { class: "login-card", novalidate: true },
      h("h1", { class: "page-title" }, "Entrar"),
      h("p", {}, "Conta: ", h("strong", {}, step.email), " ", change(step.email)),
      pass.node, error, h("div", { class: "login-actions" }, submit));
    card.addEventListener("submit", async (event) => {
      event.preventDefault();
      error.textContent = "";
      if (!pass.input.value) { error.textContent = "Digite sua senha."; pass.input.focus(); return; }
      submit.disabled = true; submit.textContent = "Entrando…";
      try {
        const result = await api("POST", "/api/auth/login", { email: step.email, password: pass.input.value });
        pass.input.value = "";
        state.user = result.student; state.csrf = result.csrfToken;
        drawUser(); renderRoute();
      } catch (e) { fail(e); submit.disabled = false; submit.textContent = "Entrar"; pass.input.select(); }
    });
    queueMicrotask(() => pass.input.focus());
  } else {
    const nameInput = h("input", { id: "name-input", class: "text-input", type: "text", name: "name", autocomplete: "name", required: true, maxlength: "80" });
    const pass = passwordField("new-password", "Crie uma senha (8 a 128 caracteres)", "new-password");
    const confirm = passwordField("confirm-password", "Repita a senha", "new-password");
    const label = step.setup ? "Definir senha" : "Criar conta";
    const submit = h("button", { class: "btn primary", type: "submit" }, label);
    card = h("form", { class: "login-card", novalidate: true },
      h("h1", { class: "page-title" }, step.setup ? "Defina sua senha" : "Criar sua conta"),
      h("p", {}, "E-mail: ", h("strong", {}, step.email), " ", change(step.email)),
      step.setup ? h("p", { class: "muted small" }, "Esta conta já existia, mas ainda não tem senha. Escolha uma senha e informe seu nome; seu progresso continua.") : null,
      step.firstUser ? h("div", { class: "goals" }, h("strong", {}, "Você será a pessoa administradora"), h("p", {}, "Ainda não há nenhuma conta neste servidor: a primeira conta criada recebe acesso à área de administração.")) : null,
      h("label", { for: "name-input", class: "field-label" }, "Seu nome"), nameInput,
      pass.node, confirm.node, error, h("div", { class: "login-actions" }, submit));
    card.addEventListener("submit", async (event) => {
      event.preventDefault();
      error.textContent = "";
      if (!nameInput.value.trim()) { error.textContent = "Informe seu nome."; nameInput.focus(); return; }
      if (pass.input.value.length < 8) { error.textContent = "A senha deve ter pelo menos 8 caracteres."; pass.input.focus(); return; }
      if (pass.input.value !== confirm.input.value) { error.textContent = "A confirmação da senha não confere."; confirm.input.focus(); return; }
      submit.disabled = true; submit.textContent = "Salvando…";
      try {
        const result = await api("POST", "/api/auth/register", { email: step.email, name: nameInput.value.trim(), password: pass.input.value, passwordConfirm: confirm.input.value });
        pass.input.value = confirm.input.value = "";
        state.user = result.student; state.csrf = result.csrfToken;
        drawUser(); renderRoute();
      } catch (e) { fail(e); submit.disabled = false; submit.textContent = label; }
    });
    queueMicrotask(() => nameInput.focus());
  }
  $("#main").replaceChildren(h("div", { class: "login-wrap" }, card));
  if (step.name === "email") $("#email-input").focus();
}

/* ---------- página inicial: grade de trilhas ---------- */
const LEVELS = { iniciante: "Iniciante", intermediario: "Intermediário", "intermediário": "Intermediário", avancado: "Avançado", "avançado": "Avançado" };
function formatMinutes(minutes) {
  if (!minutes || minutes < 1) return null;
  const total = Math.round(minutes);
  if (total < 60) return `${total} min`;
  const hours = Math.floor(total / 60), rest = total % 60;
  return rest ? `${hours} h ${rest} min` : `${hours} h`;
}
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;

async function renderHome(token) {
  setView("home");
  document.title = "Trilhas · k_study";
  drawUser();
  $("#sidebar").replaceChildren();
  state.slug = null; state.trail = null; state.block = null; state.current = null;
  const main = $("#main");
  main.replaceChildren(h("p", { class: "muted" }, "Carregando trilhas…"));
  const list = await getJson("/api/trails");
  if (token !== routeToken) return;
  state.trails = Array.isArray(list) ? list : (list?.trails || []);
  const head = h("div", { class: "home-head" },
    h("div", { class: "home-title" },
      h("h1", { class: "page-title" }, "Trilhas de estudo"),
      state.user?.isAdmin ? h("a", { class: "btn", href: "/admin/" }, "Administração") : null),
    h("p", { class: "muted" }, "Escolha uma trilha para começar ou continuar de onde parou."));
  if (!state.trails.length) {
    main.replaceChildren(head, h("div", { class: "empty-state" },
      h("strong", {}, "Nenhuma trilha encontrada."),
      h("p", {}, state.user?.isAdmin ? "Importe um pacote de trilha na área de Administração." : "Peça à pessoa administradora para importar uma trilha.")));
    return;
  }
  const grid = h("div", { class: "trail-grid" });
  for (const t of state.trails) grid.append(trailCard(t));
  main.replaceChildren(head, grid);
}

function trailCard(t) {
  const items = t.items || 0;
  const required = t.requiredItems != null ? t.requiredItems : items;
  const done = Math.min(t.done || 0, items);                          // a barra conta TODAS as aulas (obrigatórias e opcionais)
  const percent = items ? Math.round((100 * done) / items) : 0;
  const action = !done ? "Começar" : percent >= 100 ? "Revisar" : "Continuar";
  const time = formatMinutes(t.minutes);
  const stats = [plural(t.blocks || 0, "bloco", "blocos"), plural(items, "aula", "aulas"), time ? "cerca de " + time : null].filter(Boolean).join(" · ");
  const note = required !== items ? ` (${plural(required, "obrigatória", "obrigatórias")})` : "";
  const level = t.level ? (LEVELS[String(t.level).toLowerCase()] || t.level) : null;
  const cover = t.cover
    ? h("img", { class: "trail-cover", src: t.cover, alt: "", loading: "lazy", width: "1200", height: "630" })
    : h("div", { class: "trail-cover fallback", "aria-hidden": "true" }, h("span", {}, (t.title || "?").trim().charAt(0).toUpperCase()));
  return h("a", { class: "trail-card", href: trailHash(t.slug), "aria-label": `${t.title}: ${action}` },
    cover,
    h("div", { class: "trail-body" },
      h("div", { class: "trail-top" },
        level ? h("span", { class: "badge" }, level) : null,
        percent >= 100 ? h("span", { class: "badge ok" }, "Concluída") : null),
      h("h2", {}, t.title),
      t.description ? h("p", { class: "trail-desc" }, t.description) : null,
      (t.tags || []).length ? h("div", { class: "tags" }, t.tags.map((tag) => h("span", { class: "tag-chip" }, tag))) : null,
      h("p", { class: "trail-stats" }, stats + note),
      h("div", { class: "trail-progress" },
        h("div", { class: "bar", role: "progressbar", "aria-label": "Seu progresso na trilha", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(percent) },
          h("div", { style: `width:${percent}%` })),
        h("span", { class: "trail-count" }, items ? `${done} de ${items} aulas feitas (${percent}%)` : "Sem aulas ainda")),
      h("span", { class: "btn primary trail-action" }, action, " ›")));
}

/* ---------- trilha ---------- */
async function renderTrailRoute(route, token) {
  setView("trail");
  drawUser();
  if (state.slug !== route.slug || !state.trail) {
    tracker.stop();
    state.block = null; state.current = null;
    $("#main").replaceChildren(h("p", { class: "muted" }, "Carregando a trilha…"));
    $("#sidebar").replaceChildren();
    const slug = route.slug;
    const trail = await getJson(`/api/trails/${encodeURIComponent(slug)}`);
    state.slug = slug;
    mdContext.slug = slug;
    if (!(await reloadProgress())) throw new Error("não consegui carregar o seu progresso.");
    const entries = trail.blocks || [];
    const blocks = await Promise.all(entries.map(async (entry) => {
      const url = blockUrl(entry.id);
      try { return { entry, url, data: await getJson(url) }; }
      catch (error) { return { entry, url, data: null, error: error.message }; }
    }));
    if (token !== routeToken) return;
    state.trail = trail; state.blocks = blocks;
    $("#trail-name").textContent = trail.title || slug;
    document.title = `${trail.title || slug} · k_study`;
    drawBlockSelect();
  }
  if (token !== routeToken) return;
  if (!state.blocks.length) {
    $("#main").replaceChildren(h("div", { class: "empty-state" }, h("strong", {}, "Esta trilha ainda não tem blocos.")));
    return;
  }
  // bloco: o da rota; senão o primeiro que ainda tem item obrigatório pendente
  let target = state.blocks.find((b) => b.entry.id === route.block);
  if (!target) target = state.blocks.find((b) => b.data && flatten(b.data).some((i) => !i.optional && !isDoneKey(i.key))) || state.blocks.find((b) => b.data) || state.blocks[0];
  if (!state.block || state.block.id !== target.entry.id) selectBlock(target);
  if (!state.block) return;
  const item = route.block === target.entry.id && state.items.find((i) => i.id === route.item);
  const chosen = item || nextItem() || state.items[0];
  const mark = markOnNext; markOnNext = false;
  if (!item) history.replaceState(null, "", trailHash(state.slug, state.block.id, chosen?.id));
  $("#block-select").value = target.entry.id;
  await showItem(chosen, { mark: mark && !!item, track: true });
}

function selectBlock(target) {
  if (!target.data) {
    state.block = null; state.items = []; state.current = null;
    $("#sidebar").replaceChildren();
    $("#main").replaceChildren(h("div", { class: "verdict no", role: "alert" }, `Não consegui carregar o bloco "${target.entry.title}": ${target.error}`));
    return;
  }
  state.block = target.data; state.blockUrl = target.url;
  state.items = flatten(target.data);
  state.current = null;
  drawMenu();
}

function drawBlockSelect() {
  const select = $("#block-select");
  select.replaceChildren();
  for (const b of state.blocks) {
    const count = b.data ? flatten(b.data) : [];
    const done = count.filter((i) => isDoneKey(i.key)).length;
    select.append(h("option", { value: b.entry.id }, count.length ? `${b.entry.title} (${done}/${count.length})` : b.entry.title));
  }
  select.onchange = () => { location.hash = trailHash(state.slug, select.value); };
}

function flatten(block) {
  const out = [];
  for (const section of block.sections || []) for (const item of section.items || []) {
    out.push(Object.assign({}, item, { section, key: `${block.id}/${item.id}` }));
  }
  return out;
}
const isDoneKey = (key) => !!state.progress.items[key]?.done;
const isDone = (item) => isDoneKey(item.key);
const nextItem = () => state.items.find((i) => !isDone(i) && !i.optional);

/* ---------- menu lateral ---------- */
function drawMenu() {
  const nav = $("#sidebar");
  nav.replaceChildren();
  if (!state.block) return;
  const next = nextItem();
  for (const section of state.block.sections || []) {
    const keys = section.items.map((i) => ({ key: `${state.block.id}/${i.id}`, optional: i.optional }));
    const done = keys.filter(isDone).length;
    const box = h("div", { class: "section" + (section._collapsed ? " collapsed" : "") });
    const heading = h("button", { class: "section-head", type: "button", "aria-expanded": String(!section._collapsed),
      onclick: () => { section._collapsed = !section._collapsed; box.classList.toggle("collapsed"); heading.setAttribute("aria-expanded", String(!section._collapsed)); } },
      h("span", {}, section.title), h("span", { title: counterTitle(keys) }, `${done}/${section.items.length}`));
    box.append(heading);
    const list = h("div", { class: "items" });
    for (const raw of section.items) {
      const item = state.items.find((x) => x.id === raw.id);
      const kind = KINDS[raw.type] || { icon: "article", label: raw.type };
      const isNext = next && next.id === raw.id;
      const active = state.current && state.current.id === raw.id;
      list.append(h("button", {
        class: "item" + (isDone(item) ? " done" : "") + (isNext ? " next" : "") + (active ? " active" : ""),
        type: "button", "data-id": raw.id, "aria-current": active ? "page" : null,
        "aria-label": `${raw.title}. ${kind.label}. ${raw.optional ? "Opcional" : "Obrigatória"}. ${isDone(item) ? "Feito" : "Pendente"}${isNext ? ". Próxima aula" : ""}`,
        onclick: () => openByClick(item),
      },
        icon(isDone(item) ? "check_circle_filled" : "radio_button_unchecked", "status"),
        h("span", {}, h("span", { class: "title" }, icon(kind.icon, "kind"), raw.title,
          isNext ? h("span", { class: "tag-next" }, "PRÓXIMA AULA") : null),
          h("span", { class: "meta" }, requirementChip(raw), " ", [kind.label, raw.duration, raw.channel].filter(Boolean).join(" · ")))));
    }
    box.append(list);
    nav.append(box);
  }
  const total = state.items.length, finished = state.items.filter(isDone).length;
  const percent = total ? Math.round((100 * finished) / total) : 0;
  $("#overall-fill").style.width = `${percent}%`;
  $("#overall-text").textContent = `${finished}/${total} feitas`;
  $("#overall .bar").setAttribute("aria-valuenow", String(percent));
  $("#overall").title = counterTitle(state.items);
  drawBlockSelect();
  $("#block-select").value = state.block.id;
}
// "4 de 8 itens feitos (3 de 7 obrigatórios; 1 de 1 opcional)": todo item feito conta.
function counterTitle(items) {
  const done = items.filter(isDone).length;
  const required = items.filter((i) => !i.optional), optional = items.filter((i) => i.optional);
  const parts = [`${required.filter(isDone).length} de ${required.length} obrigatórios`];
  if (optional.length) parts.push(`${optional.filter(isDone).length} de ${optional.length} opcionais`);
  return `${done} de ${items.length} itens feitos (${parts.join("; ")}). Os opcionais não bloqueiam a "PRÓXIMA AULA".`;
}

function openByClick(item) {
  markOnNext = true;
  document.body.classList.remove("menu-open");
  $("#menu-btn").setAttribute("aria-expanded", "false");
  const wanted = trailHash(state.slug, state.block.id, item.id);
  if (location.hash === wanted) { renderRoute(); } else { location.hash = wanted; }
}
$("#menu-btn").addEventListener("click", () => {
  const open = document.body.classList.toggle("menu-open");
  $("#menu-btn").setAttribute("aria-expanded", String(open));
});

/* ---------- itens ---------- */
/* Obrigatória e Opcional têm cor própria E texto (nunca só cor). */
const requirementChip = (item) => h("span", { class: "chip " + (item.optional ? "optional" : "required") }, item.optional ? "Opcional" : "Obrigatória");
const questionProgress = {};            // chave do item -> {answered, total}; preenchido por renderQuestions

/* O que vem depois: o item seguinte do bloco ou, no último item, o primeiro item do próximo bloco. */
function followingOf(item) {
  const next = state.items[state.items.findIndex((x) => x.key === item.key) + 1];
  if (next) return { item: next, block: state.block.id, label: "Próxima aula ›" };
  const at = state.blocks.findIndex((b) => b.entry.id === state.block.id);
  const nb = state.blocks[at + 1];
  const first = nb?.data ? flatten(nb.data)[0] : null;
  return first ? { item: first, block: nb.entry.id, label: "Próximo bloco ›", title: nb.entry.title } : null;
}

/* Status como pílula. Clicar alterna feito/pendente, exceto em conjuntos de questões: esses só ficam feitos
   quando todas as questões forem respondidas, então a pílula só mostra o andamento. */
function statusPill(item) {
  const done = isDone(item);
  const qp = questionProgress[item.key];
  if (item.type === "questions") {
    const text = qp ? `${qp.answered}/${qp.total} respondidas` : (done ? "Concluído" : "Pendente");
    return h("span", { class: "badge status-pill " + (done ? "ok" : "pending"), title: "O conjunto de questões só fica concluído quando todas forem respondidas." },
      icon(done ? "check_circle_filled" : "radio_button_unchecked"), done ? "Concluído · " + text : text);
  }
  return h("button", { type: "button", class: "badge status-pill " + (done ? "ok" : "pending"), title: done ? "Clique para marcar como pendente" : "Clique para marcar como feito",
    onclick: () => toggleDone(item) }, icon(done ? "check_circle_filled" : "radio_button_unchecked"), done ? "Feito" : "Pendente");
}
function nextPill(item) {
  const following = followingOf(item);
  if (!following) return null;
  return h("button", { type: "button", class: "badge next-pill", title: following.item.title + (following.title ? ` (${following.title})` : ""),
    onclick: () => { markOnNext = true; location.hash = trailHash(state.slug, following.block, following.item.id); } }, following.label);
}
function refreshPills() {
  if (!state.current) return;
  for (const slot of document.querySelectorAll(".pillbar .status-slot")) slot.replaceChildren(statusPill(state.current));
}

async function showItem(item, { mark = false, track = true } = {}) {
  if (!item) { $("#main").replaceChildren(h("p", {}, "Este bloco ainda não tem aulas.")); return; }
  state.current = item;
  document.title = `${item.title} · ${state.trail?.title || "k_study"}`;
  if (track) tracker.start(state.slug, state.block.id, item.id);
  // abrir um item pelo menu marca como feito (dá para desmarcar na página); conjuntos de questões nunca são marcados ao abrir
  if (mark && !isDone(item) && item.type !== "questions") await mutate("PUT", `items/${keyPath(item.key)}`, { done: true });
  if (state.current !== item) return;
  drawMenu();
  const main = $("#main");
  const kind = KINDS[item.type] || { icon: "article", label: item.type };
  const badges = h("div", { class: "badges" }, h("span", { class: "badge" }, kind.label));
  if (item.duration) badges.append(h("span", { class: "badge" }, item.duration));
  if (item.channel) badges.append(h("span", { class: "badge" }, item.channel));
  badges.append(requirementChip(item));
  if (item.type === "video" && item.review) badges.append(h("span", { class: "badge ok", title: "A transcrição foi lida e comparada com o material; os detalhes estão em \"Conferência\", abaixo do vídeo." }, item.review.badge));
  if (item.type === "video" && !item.review) badges.append(h("span", { class: "badge warn", title: "A transcrição deste vídeo ainda não foi lida e conferida." }, "transcrição ainda não lida"));
  badges.append(h("span", { class: "pillbar top" }, h("span", { class: "status-slot" }, statusPill(item)), nextPill(item)));

  const body = h("div");
  main.replaceChildren(...[
    h("p", { class: "crumb" }, `${state.block.title} › ${item.section.title}`),
    h("h1", { class: "page-title" }, item.title),
    badges,
    item.type === "video" && !item.review
      ? h("p", { class: "muted small" }, "A transcrição deste vídeo ainda não foi lida para conferir se ele explica o que está no material. Se algo não bater, vale o material da trilha.") : null,
    item.note ? h("div", { class: "goals" }, h("strong", {}, "Nota"), h("p", { html: marked.parseInline(item.note) })) : null,
    item.goals?.length ? h("div", { class: "goals" }, h("strong", {}, item.goalsTitle || "O que você deve sair sabendo"), h("ul", {}, item.goals.map((g) => h("li", { html: marked.parseInline(g) })))) : null,
    item.warnings?.length ? h("div", { class: "goals warn" }, h("strong", {}, "Atenção: este vídeo diverge do material"), h("ul", {}, item.warnings.map((w) => h("li", { html: marked.parseInline(w) })))) : null,
    body,
  ].filter(Boolean));
  try { await renderItem(item, body); }
  catch (error) { body.append(h("div", { class: "verdict no", role: "alert" }, `Erro ao carregar este item: ${error.message}`)); }

  if (state.current !== item) return;
  const notes = h("textarea", { id: "notes", class: "notes", placeholder: "Anotações suas sobre este item (dúvidas, o que errou, o que reler)…" });
  notes.value = state.progress.notes[item.key] || "";
  let timer;
  notes.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(() => mutate("PUT", `notes/${keyPath(item.key)}`, { text: notes.value }), 500); });
  notes.addEventListener("blur", () => { clearTimeout(timer); if ((state.progress.notes[item.key] || "") !== notes.value) mutate("PUT", `notes/${keyPath(item.key)}`, { text: notes.value }); });
  main.append(h("div", { class: "pillbar bottom" }, h("span", { class: "status-slot" }, statusPill(item)), nextPill(item)),
    h("label", { class: "notes-label", for: "notes" }, "Suas anotações (salvas automaticamente)"), notes);
  if (track) window.scrollTo(0, 0);              // ao reler por sincronização, mantém a posição
}

async function toggleDone(item, value) {
  const next = value === undefined ? !isDone(item) : value;
  await mutate("PUT", `items/${keyPath(item.key)}`, { done: next });
  drawMenu();
  if (state.current && state.current.key === item.key) refreshPills();
}

async function renderItem(item, body) {
  if (item.type === "video") return renderVideo(item, body);
  if (item.type === "markdown") {
    const text = item.content != null ? item.content : await getText(itemUrl(state.block.id, item.id, "content"));
    const minutes = Math.max(1, Math.round(text.split(/\s+/).length / 180));
    const bar = $(".badges");
    if (bar) bar.insertBefore(h("span", { class: "badge" }, `~${minutes} min de leitura`), $(".badges .pillbar"));
    return renderMarkdown(text, body);
  }
  if (item.type === "pdf") {
    const url = itemUrl(state.block.id, item.id, "content");
    body.append(h("p", {}, "Este PDF abre em outra aba."),
      h("p", {}, h("a", { class: "btn primary", href: url, target: "_blank", rel: "noopener noreferrer" }, icon("open_in_new"), "Abrir o PDF em outra aba")));
    return;
  }
  if (item.type === "link") {
    if (item.description) body.append(h("div", { class: "md", html: marked.parse(item.description) }));
    const link = safeUrl(item.url);
    body.append(h("div", { class: "link-card" }, h("p", {}, item.url || ""),
      link ? h("a", { class: "btn primary", href: link, target: "_blank", rel: "noopener noreferrer" }, icon("open_in_new"), "Abrir a matéria em outra aba") : null));
    return;
  }
  if (item.type === "questions") return renderQuestions(item, body);
  body.append(h("p", {}, `Tipo de item desconhecido: ${item.type}`));
}

/* ---------- markdown seguro ---------- */
/* O conteúdo vem de arquivos que agentes escrevem: nunca é confiável. O marked é configurado para
   (1) escapar qualquer HTML bruto, (2) aceitar só links http, https, mailto, âncoras e rotas internas e
   (3) aceitar imagens somente pela rota de figuras da própria trilha. A CSP do servidor é a segunda barreira. */
const mdContext = { slug: null };
const escapeHtml = (text) => String(text ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
const SAFE_LINK = /^(https?:\/\/|mailto:|#|\/(?!\/))/i;
const FIGURE_NAME = /^[A-Za-z0-9._-]+$/;
const safeUrl = (url) => (/^https?:\/\//i.test(String(url || "").trim()) ? String(url).trim() : null);
function figureName(href) {
  const parts = String(href || "").split(/[?#]/)[0].split("/").filter(Boolean);
  const name = parts[parts.length - 1] || "";
  return parts.includes("figures") && FIGURE_NAME.test(name) ? name : null;
}
marked.use({
  gfm: true,
  renderer: {
    html(token) { return escapeHtml(typeof token === "string" ? token : token?.text ?? token?.raw ?? ""); },
    link(href, title, text) {
      const target = String(href ?? "").trim();
      if (typeof href === "object" && href !== null) return escapeHtml(href.text ?? "");          // formato novo do marked: não suportado aqui
      if (!SAFE_LINK.test(target)) return text;                                                    // sem link: só o texto
      const external = /^(https?:|mailto:)/i.test(target);
      return `<a href="${escapeHtml(target)}"${title ? ` title="${escapeHtml(title)}"` : ""}${external ? ' target="_blank" rel="noopener noreferrer"' : ""}>${text}</a>`;
    },
    image(href, title, text) {
      if (typeof href === "object" && href !== null) return escapeHtml(href.text ?? "");
      const name = figureName(href);
      if (!name || !mdContext.slug) return escapeHtml(text);                                       // imagem fora das figuras: só o texto alternativo
      return `<img src="/api/trails/${encodeURIComponent(mdContext.slug)}/figures/${encodeURIComponent(name)}" alt="${escapeHtml(text)}"${title ? ` title="${escapeHtml(title)}"` : ""} loading="lazy">`;
    },
  },
});
function renderMarkdown(text, target) {
  target.append(h("div", { class: "md", html: marked.parse(text || "") }));
}

/* ---------- vídeo ---------- */
function youtubeId(url) {
  const m = (url || "").match(/(?:v=|youtu\.be\/|embed\/)([\w-]{11})/);
  return m ? m[1] : null;
}
function mmss(seconds) { return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`; }
async function renderVideo(item, body) {
  const id = youtubeId(item.url);
  const clips = item.clips || [];
  const embedUrl = (clip, autoplay) => {
    const params = new URLSearchParams({ rel: "0" });
    if (clip?.start) params.set("start", clip.start);
    if (clip?.end) params.set("end", clip.end);
    if (autoplay) params.set("autoplay", "1");
    return `https://www.youtube-nocookie.com/embed/${id}?${params}`;
  };
  const first = clips[0] || { start: item.start, end: item.end };
  let frame;
  if (id) {
    frame = h("iframe", { src: embedUrl(first, false), title: item.title,
      allow: "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" });
    body.append(h("div", { class: "video-wrap" }, frame));
  }
  if (id && clips.length) {
    const list = h("div", { class: "clips" }, h("strong", {}, "Assista só estes trechos (clique para ir ao trecho):"));
    clips.forEach((clip, index) => {
      const button = h("button", { type: "button", class: "btn clip" + (index === 0 ? " on" : ""), onclick: () => {
        frame.src = embedUrl(clip, true);
        list.querySelectorAll(".clip").forEach((x) => x.classList.remove("on")); button.classList.add("on");
      } }, `${mmss(clip.start)} – ${mmss(clip.end)}`,
        clip.slides ? h("span", { class: "meta" }, ` slides ${clip.slides}`) : null,
        clip.note ? h("span", { class: "meta" }, ` · ${clip.note}`) : null);
      list.append(button);
    });
    const total = clips.reduce((sum, clip) => sum + (clip.end - clip.start), 0);
    list.append(h("span", { class: "muted" }, ` Total dos trechos: ${Math.round(total / 60)} min. Os tempos têm uma pequena margem de erro (poucos segundos a cerca de 15 s, conforme a fonte).`));
    body.append(list);
  }
  body.append(h("p", { class: "muted" }, id ? "Se o vídeo não abrir aqui (o autor pode ter bloqueado a incorporação), use o botão. Dica: velocidade 1,25× e legendas ligadas." : "",
    " ", safeUrl(item.url) ? h("a", { class: "btn", href: safeUrl(item.url), target: "_blank", rel: "noopener noreferrer" }, icon("open_in_new"), "Abrir no YouTube") : null));
  if (item.summary) body.append(h("div", { class: "md", html: marked.parse(item.summary) }));
  if (item.review) body.append(reviewCard(item.review));
  if (item.transcript) {
    try {
      const transcript = await getJson(itemUrl(state.block.id, item.id, "transcript"));
      const seek = (second) => { if (id && frame) { frame.src = embedUrl({ start: second }, true); frame.scrollIntoView({ behavior: "smooth", block: "center" }); } };
      body.append(transcriptCard(transcript, clips, seek));
    } catch (error) { body.append(h("p", { class: "muted small" }, "Não consegui carregar a transcrição: " + error.message)); }
  }
}

/* Conferência: o que a leitura da transcrição mostrou, comparado com o material. */
function reviewCard(review) {
  const card = h("details", { class: "card" }, h("summary", {}, "Conferência com o material (a partir da transcrição)"));
  card.append(h("p", { class: "muted small" }, "A transcrição do vídeo foi lida e comparada com os tópicos do material da trilha. A transcrição é automática, então os tempos têm uma pequena margem de erro (poucos segundos a cerca de 15 s, conforme a fonte)."));
  if (review.covers?.length) card.append(h("strong", {}, "O que o vídeo cobre"), h("ul", {}, review.covers.map((x) => h("li", { html: marked.parseInline(x) }))));
  if (review.notCovered) card.append(h("strong", {}, "O que o vídeo não cobre"), h("p", { html: marked.parseInline(review.notCovered) }));
  if (review.profile?.length) card.append(h("strong", {}, "Perfil do vídeo"), h("ul", {}, review.profile.map((x) => h("li", { html: marked.parseInline(x) }))));
  if (review.verdict) card.append(h("strong", {}, "Conclusão"), h("p", { html: marked.parseInline(review.verdict) }));
  return card;
}

/* Transcrição: mostra o começo; "Ver mais" abre tudo. Um horário leva o vídeo àquele ponto. */
function transcriptCard(transcript, clips, seek) {
  const segments = transcript.segments || [];
  const inClip = (second) => clips.some((c) => second >= c.start && second <= c.end);
  const lines = segments.map(([second, text]) =>
    h("p", { class: "line" + (inClip(second) ? " in" : "") },
      h("button", { type: "button", class: "ts", title: "Ir para este ponto do vídeo", onclick: () => seek(second) }, mmss(second)), " ", text));
  const box = h("div", { class: "lines" }, lines);
  let chars = 0, visible = 0;                       // mostra as primeiras linhas, até ~700 caracteres
  for (const [, text] of segments) { chars += text.length; visible++; if (chars > 700) break; }
  lines.forEach((line, index) => { if (index >= visible) line.classList.add("extra"); });
  let open = false;
  const toggle = h("button", { type: "button", class: "btn" }, "Ver mais");
  const card = h("div", { class: "card transcript" });
  toggle.onclick = () => { open = !open; card.classList.toggle("open", open); toggle.textContent = open ? "Ver menos" : "Ver mais"; };
  const language = transcript.lang === "pt" ? "português" : transcript.lang === "en" ? "inglês" : (transcript.lang || "idioma não informado");
  const origin = /whisper/i.test(transcript.source || "") ? "Transcrição gerada por reconhecimento de fala (Whisper) a partir do áudio do vídeo"
    : `Legenda ${transcript.generated ? "automática" : "do autor"} do YouTube`;
  card.append(h("strong", {}, "Transcrição do vídeo"),
    h("p", { class: "muted small" }, `${origin}, em ${language}; pode ter erros de reconhecimento. Clique em um horário para ir àquele ponto do vídeo.${clips.length ? " Os trechos recomendados estão em destaque." : ""}`),
    box, segments.length > visible ? toggle : null);
  return card;
}

/* ---------- questões ---------- */
// Uma questão por vez. O conjunto só fica "feito" quando todas forem respondidas; quando está completo, entrar
// no item mostra o resumo (o que você marcou, o que estava certo ou errado, com todas as explicações).
async function renderQuestions(item, body) {
  const set = await getJson(itemUrl(state.block.id, item.id, "content"));
  const total = (set.questions || []).length;
  if (!total) { body.append(h("p", { class: "muted" }, "Este conjunto ainda não tem questões.")); return; }
  const prepared = await Promise.all(set.questions.map(async (question) => {
    let prompt = question.prompt || "";
    if (!prompt && question.promptFile) prompt = "_O enunciado desta questão está em um arquivo que a interface não carrega._";
    return { question, prompt, base: null };
  }));
  const given = () => state.progress.answers[item.key] || {};
  const answeredCount = () => prepared.filter((p) => given()[p.question.id]).length;
  const rightCount = () => prepared.filter((p) => given()[p.question.id]?.correct).length;
  const firstPending = () => Math.max(0, prepared.findIndex((p) => !given()[p.question.id]));
  const wrap = h("div");
  body.append(wrap);
  let index = firstPending();
  let summary = answeredCount() === total;

  async function syncDone() {                  // feito <=> todas respondidas (nunca ao abrir)
    const all = answeredCount() === total;
    questionProgress[item.key] = { answered: answeredCount(), total };
    if (all && !isDone(item)) await toggleDone(item, true);
    else if (!all && isDone(item)) await toggleDone(item, false);
    else refreshPills();
  }
  const keyOf = (question) => `answers/${keyPath(item.key)}/${encodeURIComponent(question.id)}`;
  const actionsFor = (question) => ({
    answer: async (chosen, correct) => { await mutate("PUT", keyOf(question), { chosen, correct }); await syncDone(); draw(); },
    redo: async () => { await mutate("DELETE", keyOf(question)); await syncDone(); summary = false; index = prepared.findIndex((p) => p.question.id === question.id); draw(); },
  });

  function dots() {
    return h("div", { class: "qdots", role: "group", "aria-label": "Questões do conjunto" }, ...prepared.map((p, i) => {
      const saved = given()[p.question.id];
      const status = saved ? (saved.correct ? "acertou" : "errou") : "pendente";
      return h("button", { type: "button", class: "dot" + (saved ? (saved.correct ? " ok" : " no") : "") + (!summary && i === index ? " current" : ""),
        title: `Questão ${i + 1} (${status})`, "aria-label": `Questão ${i + 1}, ${status}`,
        onclick: () => { summary = false; index = i; draw(); } }, String(i + 1));
    }));
  }

  function drawSummary() {
    const answered = answeredCount(), right = rightCount();
    const percent = Math.round((100 * right) / total);
    const head = h("div", { class: "summary-head" },
      h("h2", {}, "Resumo das questões"),
      h("p", { class: "score" }, `Você acertou ${right} de ${total} (${percent}%).`),
      h("p", { class: "muted small" }, "Abaixo estão todas as questões, com a alternativa que você marcou, o gabarito e a explicação de cada opção."),
      h("div", { class: "summary-actions" },
        h("button", { type: "button", class: "btn small-btn", onclick: async () => { for (const p of prepared) await mutate("DELETE", keyOf(p.question)); await syncDone(); summary = false; index = 0; draw(); } }, "Refazer todas"),
        answered < total ? h("button", { type: "button", class: "btn small-btn", onclick: () => { summary = false; index = firstPending(); draw(); } }, "Voltar às questões pendentes") : null));
    wrap.append(head, dots());
    prepared.forEach((p, i) => {
      const card = h("div", { class: "question" });
      wrap.append(card);
      drawQuestion(card, p.question, i + 1, p.prompt, p.base, given()[p.question.id], actionsFor(p.question), true);
    });
    if (set.closing) wrap.append(h("div", { class: "general md", html: marked.parse(set.closing) }));
  }

  function drawOne() {
    const { question, prompt, base } = prepared[index];
    if (set.instructions && answeredCount() === 0 && index === 0) wrap.append(h("div", { class: "md", html: marked.parse(set.instructions) }));
    wrap.append(h("p", { class: "muted small" }, `Questão ${index + 1} de ${total} · respondidas: ${answeredCount()}/${total}`), dots());
    const card = h("div", { class: "question" });
    wrap.append(card);
    drawQuestion(card, question, index + 1, prompt, base, given()[question.id], actionsFor(question), false);
    const saved = given()[question.id];
    const last = index === total - 1;
    wrap.append(h("div", { class: "qnav" },
      h("button", { type: "button", class: "btn", disabled: index === 0, onclick: () => { index--; draw(); } }, "‹ Anterior"),
      answeredCount() === total
        ? h("button", { type: "button", class: "btn primary", onclick: () => { summary = true; draw(); } }, "Ver resumo")
        : h("button", { type: "button", class: "btn primary", disabled: !saved || last, title: saved ? "" : "Responda para continuar", onclick: () => {
            const next = prepared.findIndex((p, i) => i > index && !given()[p.question.id]);
            index = next >= 0 ? next : index + 1; draw(); } }, "Próxima ›")));
  }

  function draw() {
    wrap.replaceChildren();
    if (summary) drawSummary(); else drawOne();
  }
  questionProgress[item.key] = { answered: answeredCount(), total };
  refreshPills();
  draw();
}

function drawQuestion(card, question, number, prompt, base, saved, actions, inSummary) {
  const multiple = question.type === "multiple";
  card.replaceChildren();
  card.className = "question" + (saved ? " answered" : "");
  card.append(h("div", { class: "qn" }, `Questão ${number}${question.label ? " · " + question.label : ""}${multiple ? " · marque todas as corretas" : ""} `,
    inSummary && saved ? h("span", { class: "badge " + (saved.correct ? "ok" : "warn") }, saved.correct ? "acertou" : "errou") : null,
    inSummary && !saved ? h("span", { class: "badge pending" }, "não respondida") : null));
  const promptBox = h("div");
  renderMarkdown(prompt, promptBox);
  card.append(promptBox);

  const chosen = new Set(saved ? saved.chosen : []);
  const inputs = [];
  for (const option of question.options || []) {
    const input = h("input", { type: multiple ? "checkbox" : "radio", name: (inSummary ? "s-" : "q-") + question.id, value: option.id, disabled: !!saved });
    input.checked = chosen.has(option.id);
    inputs.push(input);
    const picked = chosen.has(option.id);
    let cls = "option";
    if (saved) {
      if (option.correct && picked) cls += " right";
      else if (!option.correct && picked) cls += " wrong";
      else if (option.correct && !picked) cls += " missed";
    }
    const content = h("div", { class: "body" }, h("div", {}, h("strong", {}, String(option.id).toUpperCase() + ")"), " ", h("span", { html: marked.parseInline(option.text || "") })));
    if (saved && option.explanation) {
      const tag = option.correct ? (picked ? "Correta — você marcou." : "Correta — você não marcou.") : (picked ? "Errada — você marcou." : "Errada.");
      content.append(h("div", { class: "why" }, h("span", { class: "tag" }, tag + " "), h("span", { html: marked.parseInline(option.explanation) })));
    }
    card.append(h("label", { class: cls }, input, content));
  }

  if (!saved) {
    const button = h("button", { type: "button", class: "btn primary", onclick: () => {
      const picks = inputs.filter((i) => i.checked).map((i) => i.value);
      if (!picks.length) { button.textContent = "Escolha uma alternativa primeiro"; return; }
      const rightIds = question.options.filter((o) => o.correct).map((o) => o.id).sort().join(",");
      actions.answer(picks, picks.slice().sort().join(",") === rightIds);
    } }, "Responder");
    card.append(button);
  } else {
    const mine = question.options.filter((o) => chosen.has(o.id)).map((o) => o.id.toUpperCase()).join(", ");
    const gabarito = question.options.filter((o) => o.correct).map((o) => o.id.toUpperCase()).join(", ");
    card.append(h("div", { class: "verdict " + (saved.correct ? "ok" : "no") },
      saved.correct ? `Você acertou. Marcou: ${mine}.` : `Você errou. Marcou: ${mine}. Gabarito: ${gabarito}. Leia a explicação de cada alternativa.`));
    if (question.generalExplanation) {
      const general = h("div", { class: "general" });
      renderMarkdown(question.generalExplanation, general);
      card.append(general);
    }
    card.append(h("p", {}, h("button", { type: "button", class: "btn small-btn", onclick: () => actions.redo() }, "Refazer esta questão")));
  }
}

/* ---------- início ---------- */
async function start() {
  await loadIcons();
  $("#menu-btn").replaceChildren(icon("menu"));
  try {
    await loadSession();
    const code = new URLSearchParams(location.search).get("oauth_error");      // só chaves conhecidas viram mensagem
    if (code) { state.oauthError = OAUTH_MESSAGES[code] || OAUTH_MESSAGES.failed; history.replaceState(null, "", location.pathname + location.hash); }
  } catch (error) {
    $("#main").replaceChildren(h("div", { class: "verdict no", role: "alert" }, "Não consegui iniciar: " + error.message),
      h("p", {}, "Inicie o servidor com: py main.py serve  e abra http://localhost:8765/"));
    return;
  }
  drawUser();
  await renderRoute();
}
start();
