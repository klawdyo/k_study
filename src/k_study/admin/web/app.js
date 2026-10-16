/* Área administrativa do k_study (servida em /admin/, só para administradores). Sem bibliotecas: gráficos em SVG escritos à mão.
   Segurança: nenhum innerHTML e nenhum script inline; todo dado do servidor entra como texto (nós criados com h() e s()).
   Toda escrita envia X-CSRF-Token (vem de GET /api/auth/me). */
"use strict";

const $ = (sel, root = document) => root.querySelector(sel);
const main = $("#main");
const TYPE_LABEL = { video: "Vídeo", markdown: "Leitura", pdf: "PDF", link: "Link", questions: "Questões" };
const SVG_NS = "http://www.w3.org/2000/svg";
let redraw = [];            // funções que redesenham os gráficos ao redimensionar
let token = 0;              // descarta respostas de rotas que já foram abandonadas
const session = { user: null, csrf: null };

/* ---------- construção de nós (sempre texto, nunca HTML) ---------- */
function build(node, attrs, children) {
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value == null || value === false) continue;
    if (key === "class") node.setAttribute("class", value);
    else if (key.startsWith("on") && typeof value === "function") node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? "" : String(value));
  }
  for (const child of children.flat(Infinity)) {
    if (child == null || child === false) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}
const h = (tag, attrs, ...children) => build(document.createElement(tag), attrs, children);
const s = (tag, attrs, ...children) => build(document.createElementNS(SVG_NS, tag), attrs, children);
const setChildren = (el, ...nodes) => el.replaceChildren(...nodes.flat(Infinity).filter((n) => n != null && n !== false));
const code = (text) => h("code", {}, text);

/* ---------- utilidades ---------- */
function fmtTime(sec) {
  sec = Math.round(sec || 0);
  if (sec < 60) return `${sec} s`;
  if (sec < 3600) { const m = Math.floor(sec / 60), r = sec % 60; return r ? `${m} min ${r} s` : `${m} min`; }
  const hh = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60);
  return `${hh} h ${String(m).padStart(2, "0")} min`;
}
function fmtHours(sec) {            // total acumulado, para os cartões
  sec = sec || 0;
  if (sec < 3600) return { v: String(Math.round(sec / 60)), u: "min" };
  const hh = sec / 3600;
  return { v: hh >= 100 ? String(Math.round(hh)) : hh.toFixed(1).replace(".", ","), u: "h" };
}
const pct = (r, d = 0) => (r == null ? "—" : `${(r * 100).toFixed(d).replace(".", ",")}%`);
const fmtInt = (n) => (n ?? 0).toLocaleString("pt-BR");
function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return isNaN(d) ? "—" : d.toLocaleDateString("pt-BR");
}
function fmtWhen(iso) {
  if (!iso) return "nunca";
  const d = new Date(iso);
  if (isNaN(d)) return "—";
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 90) return "agora";
  if (diff < 3600) return `há ${Math.round(diff / 60)} min`;
  if (diff < 86400) return `há ${Math.round(diff / 3600)} h`;
  const days = Math.floor(diff / 86400);
  if (days === 1) return "ontem";
  if (days < 30) return `há ${days} dias`;
  return fmtDate(iso);
}
const plural = (n, one, many) => `${fmtInt(n)} ${n === 1 ? one : many}`;
const num = (v) => (v == null ? -Infinity : v);
const personName = (p) => p.name || "(sem nome)";

function meter(rate, kind) {
  if (rate == null) return h("span", { class: "muted" }, "—");
  const w = Math.max(0, Math.min(1, rate)) * 100;
  const fill = h("div", { class: "meter-fill " + (kind || "") });
  fill.style.width = `${w.toFixed(1)}%`;
  return h("div", { class: "meter" }, h("div", { class: "meter-track" }, fill), h("span", { class: "meter-val" }, pct(rate)));
}
const accKind = (r) => (r == null ? "" : r >= 0.75 ? "good" : r >= 0.5 ? "warn" : "bad");
/* Nome e e-mail sempre juntos. */
const personLabel = (p, href) => h("span", { class: "person" },
  href ? h("a", { class: "pname", href }, personName(p)) : h("span", { class: "pname" }, personName(p)),
  h("span", { class: "pmail" }, p.email));

/* ---------- API ---------- */
class ApiError extends Error {
  constructor(status, code, message, extra) { super(message); this.status = status; this.code = code; this.extra = extra || {}; }
}
async function api(path, opts = {}, retried = false) {
  const options = { cache: "no-store", ...opts, headers: { ...(opts.headers || {}) } };
  if (options.method && options.method !== "GET") options.headers["X-CSRF-Token"] = session.csrf || "";
  let res;
  try { res = await fetch(path, options); }
  catch (e) { throw new ApiError(0, "network", "Não foi possível falar com o servidor. Ele ainda está rodando?"); }
  let data = null;
  try { data = await res.json(); } catch (e) { /* corpo vazio */ }
  if (!res.ok) {
    if (res.status === 403 && data?.error === "csrf_failed" && !retried) { await loadSession(); return api(path, opts, true); }
    throw new ApiError(res.status, data?.error || "error", data?.message || `Erro ${res.status}`, data || {});
  }
  return data;
}
const postJson = (path, body) => api(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
async function loadSession() {
  const me = await api("/api/auth/me");
  session.user = me.student; session.csrf = me.csrfToken;
  return me;
}

/* ---------- tema ---------- */
function themeIsDark() {
  const t = document.documentElement.dataset.theme;
  return t ? t === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
}
function paintThemeButton() { $("#theme-btn").textContent = themeIsDark() ? "Tema claro" : "Tema escuro"; }
$("#theme-btn").addEventListener("click", () => {
  const next = themeIsDark() ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("kstudy-admin-theme", next); } catch (e) { /* sem armazenamento */ }
  paintThemeButton();
});
matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", paintThemeButton);

/* ---------- dica flutuante: o texto vem em data-tip, linhas separadas por quebra; a primeira vai em negrito ---------- */
const tip = $("#tip");
document.addEventListener("pointermove", (e) => {
  const el = e.target.closest?.("[data-tip]");
  if (!el) { tip.hidden = true; return; }
  const lines = el.dataset.tip.split("\n");
  setChildren(tip, h("b", {}, lines[0]), lines.slice(1).map((line) => [h("br"), line]));
  tip.hidden = false;
  const r = tip.getBoundingClientRect();
  let x = e.clientX + 14, y = e.clientY + 16;
  if (x + r.width > innerWidth - 8) x = e.clientX - r.width - 14;
  if (y + r.height > innerHeight - 8) y = e.clientY - r.height - 12;
  tip.style.left = `${Math.max(8, x)}px`; tip.style.top = `${Math.max(8, y)}px`;
});
document.addEventListener("pointerleave", () => { tip.hidden = true; }, true);
addEventListener("scroll", () => { tip.hidden = true; }, { passive: true });

/* ---------- gráficos ---------- */
function niceMax(max, ticks = 4) {
  if (max <= 0) return { max: ticks, step: 1 };
  const raw = max / ticks, mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((x) => x >= raw);
  return { max: step * ticks, step };
}
function dayLabel(date) { const [, m, d] = date.split("-"); return `${d}/${m}`; }
const f1 = (n) => +n.toFixed(1);

/** Gráfico de colunas (tempo por dia). series: [{date, value, visits}] */
function barChart(el, series, label) {
  const draw = () => {
    const W = Math.max(280, el.clientWidth), H = 220, L = 46, R = 8, T = 10, B = 26;
    const maxRaw = Math.max(...series.map((d) => d.value), 0);
    const useHours = maxRaw >= 7200, div = useHours ? 3600 : 60, unit = useHours ? "h" : "min";
    const { max, step } = niceMax(maxRaw / div);
    const iw = W - L - R, ih = H - T - B, bw = iw / series.length;
    const g = [];
    for (let v = 0; v <= max + 1e-9; v += step) {
      const y = T + ih - (v / max) * ih;
      g.push(s("line", { class: "grid-line", x1: L, x2: W - R, y1: y, y2: y }),
        s("text", { x: L - 8, y: y + 4, "text-anchor": "end" }, `${(+v.toFixed(2)).toLocaleString("pt-BR")} ${unit}`));
    }
    const every = W < 480 ? 7 : 5;
    series.forEach((d, i) => {
      const x = L + i * bw, bh = max ? (d.value / div / max) * ih : 0;
      const col = s("g", { class: "col", "data-tip": `${dayLabel(d.date)}\n${fmtTime(d.value)} estudados\n${plural(d.visits, "visita", "visitas")}` },
        s("rect", { class: "hit", x, y: T, width: bw, height: ih }),
        d.value ? s("rect", { class: "bar", x: f1(x + bw * 0.14), y: f1(T + ih - bh), width: f1(Math.max(2, bw * 0.72)), height: f1(Math.max(2, bh)), rx: 3 }) : null);
      g.push(col);
      if ((series.length - 1 - i) % every === 0) g.push(s("text", { x: x + bw / 2, y: H - 6, "text-anchor": "middle" }, dayLabel(d.date)));
    });
    setChildren(el, s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": label }, g));
  };
  draw(); redraw.push(draw);
}

/** Linha com área (alunos ativos por dia). */
function lineChart(el, series, label) {
  const draw = () => {
    const W = Math.max(280, el.clientWidth), H = 220, L = 34, R = 12, T = 10, B = 26;
    const maxRaw = Math.max(...series.map((d) => d.value), 0);
    const { max, step } = niceMax(Math.max(maxRaw, 4), 4);
    const iw = W - L - R, ih = H - T - B, n = series.length;
    const px = (i) => L + (n === 1 ? iw / 2 : (i / (n - 1)) * iw), py = (v) => T + ih - (v / max) * ih;
    const g = [];
    for (let v = 0; v <= max + 1e-9; v += step) {
      const y = py(v);
      g.push(s("line", { class: "grid-line", x1: L, x2: W - R, y1: y, y2: y }), s("text", { x: L - 8, y: y + 4, "text-anchor": "end" }, Math.round(v)));
    }
    const pts = series.map((d, i) => `${px(i).toFixed(1)},${py(d.value).toFixed(1)}`);
    g.push(s("polygon", { class: "area", points: `${px(0)},${T + ih} ${pts.join(" ")} ${px(n - 1)},${T + ih}` }), s("polyline", { class: "line", points: pts.join(" ") }));
    const every = W < 480 ? 7 : 5, cw = iw / n;
    series.forEach((d, i) => {
      g.push(s("g", { class: "col", "data-tip": `${dayLabel(d.date)}\n${plural(d.value, "aluno ativo", "alunos ativos")}` },
        s("rect", { class: "hit", x: px(i) - cw / 2, y: T, width: cw, height: ih }),
        d.value ? s("circle", { class: "dot", cx: px(i), cy: py(d.value), r: 3.5 }) : null));
      if ((n - 1 - i) % every === 0) g.push(s("text", { x: px(i), y: H - 6, "text-anchor": "middle" }, dayLabel(d.date)));
    });
    setChildren(el, s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": label }, g));
  };
  draw(); redraw.push(draw);
}
let resizeTimer;
addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => redraw.forEach((f) => f()), 120); });

/* ---------- tabela ordenável ---------- */
function sortableTable(container, { columns, rows, sortKey, sortDir = -1, rowHref, filter, emptyText }) {
  let st = { key: sortKey, dir: sortDir, text: "" };
  const render = () => {
    const col = columns.find((c) => c.key === st.key);
    let shown = rows.filter((r) => !st.text || filter(r).toLowerCase().includes(st.text));
    if (col) {
      shown = shown.slice().sort((a, b) => {
        const va = col.sort(a), vb = col.sort(b);
        const c = typeof va === "string" ? va.localeCompare(vb, "pt-BR") : va - vb;
        return c * st.dir || String(a.email ?? "").localeCompare(String(b.email ?? ""));
      });
    }
    const head = columns.map((c) => {
      const active = c.key === st.key;
      return h("th", { scope: "col", class: c.num ? "num" : "", "aria-sort": active ? (st.dir > 0 ? "ascending" : "descending") : null },
        h("button", { type: "button", onclick: () => {
          st = { ...st, key: c.key, dir: st.key === c.key ? -st.dir : (c.num ? -1 : 1) };
          render();
          container.querySelector(`th:nth-child(${columns.indexOf(c) + 1}) button`)?.focus();
        } }, c.label, h("span", { "aria-hidden": "true" }, active ? (st.dir > 0 ? "▲" : "▼") : "")));
    });
    const body = shown.map((r) => {
      const href = rowHref ? rowHref(r) : "";
      const tr = h("tr", { class: href ? "link" : null }, columns.map((c) => h("td", { class: `${c.num ? "num" : ""} ${c.cls || ""}`.trim() }, c.render(r))));
      if (href) tr.addEventListener("click", (e) => { if (!e.target.closest("a")) location.hash = href; });
      return tr;
    });
    setChildren(container,
      h("div", { class: "table-wrap" }, h("table", {}, h("thead", {}, h("tr", {}, head)), h("tbody", {}, body))),
      shown.length ? null : h("p", { class: "mini-empty" }, emptyText || "Nada encontrado."),
      h("p", { class: "table-note" }, plural(shown.length, "linha", "linhas") + (st.text ? ` de ${fmtInt(rows.length)}` : "")));
  };
  render();
  return { setFilter(t) { st.text = t.trim().toLowerCase(); render(); } };
}

/* ---------- peças de tela ---------- */
const kpi = (label, value, note) =>
  h("div", { class: "card kpi" }, h("span", { class: "kpi-label" }, label), h("span", { class: "kpi-value" }, value), note ? h("span", { class: "kpi-note" }, note) : null);
const loading = () => setChildren(main, h("div", { class: "grid kpis" }, h("div", { class: "skeleton" }), h("div", { class: "skeleton" }), h("div", { class: "skeleton" })));
const emptyState = (title, ...body) => h("div", { class: "card empty" }, h("h2", {}, title), body);
function errorView(err) {
  const title = err.code === "database_missing" || err.code === "database_error" ? "O banco de dados ainda não está pronto" : "Algo deu errado";
  setChildren(main, emptyState(title, h("p", {}, err.message), h("p", {}, h("button", { class: "btn", type: "button", onclick: route }, "Tentar de novo"))));
}
function head(title, sub, tools, crumbs) {
  return h("div", { class: "page-head" },
    h("div", {}, crumbs ? h("div", { class: "crumbs" }, crumbs) : null, h("h1", {}, title), sub ? h("p", {}, sub) : null),
    tools ? h("div", {}, tools) : null);
}
const trailLink = (slug) => `#/trails/${encodeURIComponent(slug)}`;
const card = (title, note, ...body) => h("section", { class: "card" }, h("div", { class: "card-head" }, h("h2", {}, title), note ? h("span", { class: "muted" }, note) : null), body);

/* ---------- telas ---------- */
async function viewOverview() {
  const d = await api("/api/admin/overview");
  const t = d.totals, hrs = fmtHours(t.seconds);
  if (!t.students) {
    setChildren(main, head("Visão geral", "Estatísticas de estudo de todos os alunos."),
      emptyState("Nenhum aluno ainda", h("p", {}, "Assim que alguém abrir o servidor e criar uma conta, as estatísticas aparecem aqui."),
        h("p", {}, plural(t.trails, "trilha disponível", "trilhas disponíveis") + " para estudar.")));
    return;
  }
  const quickRate = t.visits ? t.quick_visits / t.visits : null;
  const chTime = h("div", { class: "chart" }), chActive = h("div", { class: "chart" });
  setChildren(main,
    head("Visão geral", `Atualizado ${fmtWhen(d.generated_at)}. Datas em UTC.`, h("button", { class: "btn", type: "button", onclick: route }, "Atualizar")),
    h("section", { class: "grid kpis", "aria-label": "Resumo" },
      kpi("Alunos", fmtInt(t.students), "cadastrados"),
      kpi("Ativos em 7 dias", fmtInt(t.active_7d), t.students ? `${pct(t.active_7d / t.students)} dos alunos` : ""),
      kpi("Tempo estudado", [hrs.v, h("small", {}, ` ${hrs.u}`)], `${fmtTime(t.students ? t.seconds / t.students : 0)} por aluno`),
      kpi("Visitas", fmtInt(t.visits), quickRate == null ? "" : `${pct(quickRate)} só abriram e saíram`),
      kpi("Trilhas", fmtInt(t.trails), t.answers ? `${pct(t.accuracy)} de acerto em ${fmtInt(t.answers)} respostas` : "Sem respostas ainda")),
    h("section", { class: "grid cols-2" }, card("Tempo estudado por dia", "últimos 30 dias", chTime), card("Alunos ativos por dia", "últimos 30 dias", chActive)),
    h("section", { class: "grid cols-3" },
      card("Conclusão por trilha", "só quem iniciou", trailRank(d.trails)),
      card("Questões mais erradas", "mín. 2 respostas", hardList(d.hardest_questions, true)),
      card("Aulas com mais abandono", "visitas < 10 s", abandonList(d.abandoned_items))),
    card("Atividade recente", null, recentFeed(d.recent)));
  barChart(chTime, d.daily.map((x) => ({ date: x.date, value: x.seconds, visits: x.visits })), "Tempo estudado por dia nos últimos 30 dias");
  lineChart(chActive, d.daily.map((x) => ({ date: x.date, value: x.active_students })), "Alunos ativos por dia nos últimos 30 dias");
}
function trailRank(list) {
  if (!list.length) return h("p", { class: "mini-empty" }, "Nenhuma trilha indexada ainda. Importe um pacote em ", h("a", { href: "#/import" }, "Importar trilha"), ".");
  return h("ol", { class: "rank" }, list.map((t) => h("li", {},
    h("div", { class: "rank-top" }, h("a", { href: trailLink(t.slug) }, t.title)), meter(t.avg_completion, ""),
    h("span", { class: "rank-sub" }, plural(t.students, "aluno iniciou", "alunos iniciaram")))));
}
function hardList(list, showTrail) {
  if (!list.length) return h("p", { class: "mini-empty" }, "Ainda não há erros suficientes para listar.");
  return h("ol", { class: "rank" }, list.map((q) => h("li", {},
    h("div", { class: "rank-top" }, h("span", {}, `${q.item_title} · ${q.question_id}`)), meter(q.error_rate, "bad"),
    h("span", { class: "rank-sub" }, `${showTrail ? q.trail_title + " · " : ""}${q.wrong} erros em ${q.answers} respostas`))));
}
function abandonList(list) {
  if (!list.length) return h("p", { class: "mini-empty" }, "Nenhuma aula com abandono relevante (precisa de 3 visitas ou mais).");
  return h("ol", { class: "rank" }, list.map((a) => h("li", {},
    h("div", { class: "rank-top" }, h("a", { href: trailLink(a.trail) }, a.title)), meter(a.abandon_rate, "warn"),
    h("span", { class: "rank-sub" }, `${a.trail_title} · ${a.quick_visits} de ${a.visits} visitas`))));
}
function recentFeed(list) {
  if (!list.length) return h("p", { class: "mini-empty" }, "Nenhuma atividade registrada.");
  const verb = {
    visit: (e) => ["abriu ", h("b", {}, e.title), ` (${e.detail})`],
    answer: (e) => [`${e.detail} uma questão de `, h("b", {}, e.title)],
    done: (e) => ["concluiu ", h("b", {}, e.title)],
  };
  return h("ul", { class: "feed" }, list.map((e) => h("li", {},
    h("span", { class: `dot-kind ${e.kind}`, "aria-hidden": "true" }),
    h("span", { class: "what" }, personLabel(e, `#/students/${e.student_id}`), " ", verb[e.kind](e), " ", h("span", { class: "muted" }, `· ${e.trail_title}`)),
    h("span", { class: "when" }, fmtWhen(e.at)))));
}

async function viewStudents() {
  const { students } = await api("/api/admin/students");
  if (!students.length) {
    setChildren(main, head("Alunos", "Quem já entrou para estudar."), emptyState("Nenhum aluno cadastrado", h("p", {}, "Os alunos aparecem aqui depois de criarem a conta na interface de estudo.")));
    return;
  }
  const table = h("div");
  const filter = h("input", { type: "search", placeholder: "Filtrar por nome ou e-mail", "aria-label": "Filtrar alunos por nome ou e-mail" });
  setChildren(main, head("Alunos", `${plural(students.length, "aluno cadastrado", "alunos cadastrados")}.`),
    h("div", { class: "card" }, h("div", { class: "toolbar" }, filter), table));
  const t = sortableTable(table, {
    rows: students, sortKey: "last", sortDir: -1, filter: (r) => `${r.name} ${r.email}`, rowHref: (r) => `#/students/${r.id}`, emptyText: "Nenhum aluno com esse nome ou e-mail.",
    columns: [
      { key: "email", label: "Aluno", sort: (r) => (r.name || r.email).toLowerCase(), render: (r) => personLabel(r, `#/students/${r.id}`) },
      { key: "created", label: "Cadastro", sort: (r) => r.created_at || "", render: (r) => fmtDate(r.created_at), cls: "small" },
      { key: "last", label: "Última atividade", sort: (r) => r.last_activity || "", render: (r) => fmtWhen(r.last_activity), cls: "small" },
      { key: "time", label: "Tempo", num: true, sort: (r) => r.seconds, render: (r) => fmtTime(r.seconds) },
      { key: "done", label: "Itens feitos", num: true, sort: (r) => r.items_done, render: (r) => fmtInt(r.items_done) },
      { key: "acc", label: "Acerto", num: true, sort: (r) => num(r.accuracy),
        render: (r) => (r.answers ? [h("span", { class: `pill ${accKind(r.accuracy)}` }, pct(r.accuracy)), " ", h("span", { class: "muted" }, `${r.correct}/${r.answers}`)] : h("span", { class: "muted" }, "—")) },
    ],
  });
  filter.addEventListener("input", (e) => t.setFilter(e.target.value));
}

async function viewStudent(id) {
  let d;
  try { d = await api(`/api/admin/students/${encodeURIComponent(id)}`); }
  catch (e) { if (e.status === 404) { setChildren(main, emptyState("Aluno não encontrado", h("p", {}, h("a", { href: "#/students" }, "Voltar para a lista de alunos")))); return; } throw e; }
  const st = d.student, quick = st.visits ? st.quick_visits / st.visits : null;
  setChildren(main,
    head(personName(st), [st.email, ` · cadastrado em ${fmtDate(st.created_at)} · última atividade ${fmtWhen(st.last_activity)}`], null,
      [h("a", { href: "#/students" }, "Alunos"), " / ", st.email]),
    h("section", { class: "grid kpis" }, kpi("Tempo estudado", fmtTime(st.seconds)), kpi("Visitas", fmtInt(st.visits)),
      kpi("Só abriu e saiu", fmtInt(st.quick_visits), quick == null ? "" : `${pct(quick)} das visitas`), kpi("Itens feitos", fmtInt(st.items_done)),
      kpi("Acerto", st.answers ? pct(st.accuracy) : "—", st.answers ? `${st.correct} de ${st.answers} respostas` : "Sem respostas")),
    d.trails.length ? d.trails.map(studentTrail) : emptyState("Sem atividade em trilhas", h("p", {}, "Este aluno ainda não abriu nenhuma aula.")));
}
function studentTrail(tr) {
  const maxSec = Math.max(1, ...tr.items.map((i) => i.seconds));
  let lastBlock = null;
  const rows = [];
  for (const i of tr.items) {
    if (i.block_id !== lastBlock) { lastBlock = i.block_id; rows.push(h("tr", { class: "group-row" }, h("td", { colspan: 6 }, i.block_title))); }
    const qs = i.questions.length
      ? [h("span", { class: "qs" }, i.questions.map((q) => h("span", { class: "q" + (q.correct ? "" : " wrong"), "data-tip": `${q.question_id}\n${q.correct ? "Acertou" : "Errou"} · marcou ${q.chosen.join(", ") || "—"}` }))),
        " ", h("span", { class: "muted" }, `${i.questions.filter((q) => q.correct).length}/${i.questions.length}`)]
      : h("span", { class: "muted" }, "—");
    const fill = h("div", { class: "meter-fill" });
    fill.style.width = `${(i.seconds / maxSec * 100).toFixed(1)}%`;
    const val = h("span", { class: "meter-val" }, i.seconds ? fmtTime(i.seconds) : "—");
    val.style.minWidth = "5.5em";
    rows.push(h("tr", {},
      h("td", {}, i.title, i.optional ? [" ", h("span", { class: "pill" }, "opcional")] : null, h("div", { class: "rank-sub" }, `${TYPE_LABEL[i.type] || i.type} · ${i.section || ""}`)),
      h("td", {}, i.done ? h("span", { class: "pill good" }, "feito") : h("span", { class: "pill" }, "pendente")),
      h("td", { class: "num" }, h("div", { class: "meter" }, h("div", { class: "meter-track" }, fill), val)),
      h("td", { class: "num" }, i.visits || "—"),
      h("td", { class: "num" }, i.quick_visits ? h("span", { class: "pill warn" }, i.quick_visits) : "—"),
      h("td", {}, qs)));
  }
  const bar = h("div", { class: "meter-fill good" });
  bar.style.width = `${((tr.completion || 0) * 100).toFixed(1)}%`;
  const tall = h("div", { class: "meter tall" }, h("div", { class: "meter-track" }, bar), h("span", { class: "meter-val" }, pct(tr.completion)));
  tall.style.marginBottom = "14px";
  const section = h("section", { class: "card" },
    h("div", { class: "card-head" }, h("h2", {}, h("a", { href: trailLink(tr.slug) }, tr.title)),
      h("span", { class: "muted" }, `${tr.required_done} de ${tr.required_items} itens obrigatórios · ${fmtTime(tr.seconds)}${tr.answers ? ` · acerto ${pct(tr.accuracy)}` : ""}`)),
    tall,
    h("div", { class: "table-wrap" }, h("table", {},
      h("thead", {}, h("tr", {}, h("th", { scope: "col" }, "Item"), h("th", { scope: "col" }, "Estado"), h("th", { scope: "col", class: "num" }, "Tempo"),
        h("th", { scope: "col", class: "num" }, "Visitas"), h("th", { scope: "col", class: "num" }, "Só abriu e saiu"), h("th", { scope: "col" }, "Questões"))),
      h("tbody", {}, rows))));
  section.style.marginBottom = "16px";
  return section;
}

/* ---------- trilhas: lista com capa, estado, ativar e desativar ---------- */
function coverBox(t) {
  return t.cover
    ? h("img", { class: "tcover", src: t.cover, alt: "", loading: "lazy" })
    : h("div", { class: "tcover fallback", "aria-hidden": "true" }, (t.title || "?").trim().charAt(0).toUpperCase());
}
async function viewTrails() {
  const { trails } = await api("/api/admin/trails");
  if (!trails.length) {
    setChildren(main, head("Trilhas", "Os cursos disponíveis para os alunos."),
      emptyState("Nenhuma trilha ainda", h("p", {}, "Importe um pacote zip de trilha para começar."), h("p", {}, h("a", { class: "btn primary", href: "#/import" }, "Importar trilha"))));
    return;
  }
  setChildren(main,
    head("Trilhas", `${plural(trails.length, "trilha", "trilhas")} no catálogo.`, h("a", { class: "btn primary", href: "#/import" }, "Importar trilha")),
    h("div", { class: "grid cols-2" }, trails.map((t) => {
      const toggle = h("button", { class: "btn", type: "button", onclick: async () => {
        const next = !t.active;
        const question = next ? `Reativar "${t.title}"? Os alunos voltam a vê-la.` : `Desativar "${t.title}"? Os alunos deixam de vê-la (o progresso deles fica guardado).`;
        if (!confirm(question)) return;
        toggle.disabled = true;
        try { await postJson(`/api/admin/trails/${encodeURIComponent(t.slug)}/active`, { active: next }); route(); }
        catch (e) { toggle.disabled = false; alert(e.message); }
      } }, t.active ? "Desativar" : "Reativar");
      return h("div", { class: "card trail-card" + (t.active ? "" : " off") },
        coverBox(t),
        h("div", { class: "tbody" },
          h("div", { class: "ttitle" }, h("h3", {}, h("a", { href: trailLink(t.slug) }, t.title)),
            h("span", { class: "pill " + (t.active ? "good" : "warn") }, t.active ? "Ativa" : "Desativada")),
          t.description ? h("p", { class: "muted tdesc" }, t.description) : null,
          meter(t.avg_completion),
          h("div", { class: "trail-meta" }, h("span", {}, plural(t.students, "aluno", "alunos")), h("span", {}, `${plural(t.blocks, "bloco", "blocos")} · ${plural(t.items, "item", "itens")}`),
            h("span", {}, `${fmtTime(t.avg_seconds)} por aluno`), h("span", {}, t.accuracy == null ? "sem respostas" : `acerto ${pct(t.accuracy)}`)),
          h("div", {}, toggle)));
    })));
}

/* ---------- importar trilha e baixar specs ---------- */
function uploadZip(file, replace, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `/api/admin/trails/import?replace=${replace ? 1 : 0}`);
    xhr.setRequestHeader("Content-Type", "application/zip");
    xhr.setRequestHeader("X-CSRF-Token", session.csrf || "");
    xhr.responseType = "text";
    xhr.upload.addEventListener("progress", (e) => { if (e.lengthComputable) onProgress(e.loaded / e.total); });
    xhr.addEventListener("load", () => {
      let data = null;
      try { data = JSON.parse(xhr.responseText); } catch (e) { /* sem corpo */ }
      if (xhr.status >= 200 && xhr.status < 300) resolve(data);
      else reject(new ApiError(xhr.status, data?.error || "error", data?.message || `Erro ${xhr.status}`, data || {}));
    });
    xhr.addEventListener("error", () => reject(new ApiError(0, "network", "A conexão caiu durante o envio.")));
    xhr.send(file);
  });
}
function viewImport() {
  const input = h("input", { type: "file", accept: ".zip,application/zip", id: "zip-file", class: "visually-hidden" });
  const picked = h("p", { class: "muted", id: "picked" }, "Nenhum arquivo escolhido.");
  const replace = h("input", { type: "checkbox", id: "replace" });
  const bar = h("div", { class: "meter-fill" });
  const track = h("div", { class: "meter-track" }, bar);
  const progress = h("div", { class: "meter", hidden: true }, track, h("span", { class: "meter-val", id: "up-pct" }, "0%"));
  const result = h("div", { class: "import-result", role: "status", "aria-live": "polite" });
  const send = h("button", { class: "btn primary", type: "button", disabled: true }, "Enviar pacote");
  let file = null;
  const choose = (f) => {
    if (!f) return;
    file = f;
    picked.textContent = `${f.name} · ${(f.size / (1024 * 1024)).toFixed(1).replace(".", ",")} MB`;
    send.disabled = false;
    setChildren(result);
  };
  const drop = h("label", { class: "dropzone", for: "zip-file" }, h("strong", {}, "Escolha o arquivo .zip ou arraste-o até aqui"), picked, input);
  for (const name of ["dragenter", "dragover"]) drop.addEventListener(name, (e) => { e.preventDefault(); drop.classList.add("over"); });
  for (const name of ["dragleave", "drop"]) drop.addEventListener(name, (e) => { e.preventDefault(); drop.classList.remove("over"); });
  drop.addEventListener("drop", (e) => choose(e.dataTransfer?.files?.[0]));
  input.addEventListener("change", () => choose(input.files[0]));
  send.addEventListener("click", async () => {
    if (!file) return;
    send.disabled = true; progress.hidden = false; bar.style.width = "0%";
    setChildren(result);
    try {
      const out = await uploadZip(file, replace.checked, (r) => { bar.style.width = `${(r * 100).toFixed(0)}%`; $("#up-pct").textContent = pct(r); });
      bar.style.width = "100%"; $("#up-pct").textContent = "100%";
      setChildren(result, h("div", { class: "notice good" }, h("strong", {}, `Trilha importada: ${out.slug}${out.replaced ? " (substituiu a anterior)" : ""}.`),
        out.warnings?.length ? [h("p", {}, "Avisos (não impedem o uso; vale conferir):"), h("ul", {}, out.warnings.map((w) => h("li", {}, w)))] : h("p", {}, "Sem avisos."),
        h("p", {}, h("a", { href: trailLink(out.slug) }, "Ver a trilha"), " · ", h("a", { href: "#/trails" }, "Ir para a lista de trilhas"))));
    } catch (e) {
      const problems = e.extra?.problems;
      setChildren(result, h("div", { class: "notice bad", role: "alert" }, h("strong", {}, e.message),
        problems?.length ? [h("p", {}, "O pacote foi recusado por estes motivos:"), h("ul", {}, problems.map((p) => h("li", {}, p)))] : null));
      send.disabled = false;
    }
  });
  const specs = h("a", { class: "btn", href: "/api/admin/specs.zip", download: "k_study-specs.zip" }, "Baixar specs para criar uma trilha");
  setChildren(main, head("Importar trilha", "Envie o pacote .zip que o agente de IA gerou, ou baixe as instruções para criar uma trilha nova."),
    h("section", { class: "grid cols-2" },
      card("Importar um pacote de trilha", "arquivo .zip",
        drop,
        h("label", { class: "check", for: "replace" }, replace, " Substituir se a trilha já existir (o progresso dos alunos é mantido)"),
        h("div", { class: "actions" }, send), progress, result),
      card("Criar uma trilha nova", "feito fora do servidor",
        h("p", {}, "O servidor não cria trilhas: quem cria é um agente de IA rodando no seu computador. Para começar:"),
        h("ol", { class: "steps" },
          h("li", {}, "Baixe o zip das specs abaixo."),
          h("li", {}, "Abra um agente de IA (por exemplo, o Claude Code) numa pasta vazia e descompacte o zip nela."),
          h("li", {}, "Peça a criação da trilha, dizendo o assunto e enviando o seu material. O agente segue as specs: entrevista você, baixa e transcreve os vídeos com o k_transcriptor (projeto de apoio) e gera a pasta da trilha."),
          h("li", {}, ["Quando a trilha estiver pronta, o agente roda ", code("kstudy pack SLUG"), " e gera um arquivo .zip."]),
          h("li", {}, "Volte aqui e envie esse .zip em \"Importar um pacote de trilha\".")),
        h("div", { class: "actions" }, specs))));
}

/* ---------- mapa de calor de uma trilha ---------- */
const METRICS = {
  completion: { label: "Conclusão", get: (i) => i.completion, tone: "accent", text: (v) => pct(v), hint: "alunos que concluíram" },
  abandon: { label: "Abandono", get: (i) => i.abandon_rate, tone: "warn", text: (v) => pct(v), hint: "visitas < 10 s" },
  time: { label: "Tempo médio", get: (i) => (i.students_opened ? i.avg_seconds : null), tone: "teal", text: (v) => fmtTime(v), hint: "por aluno que abriu" },
  accuracy: { label: "Acerto", get: (i) => i.accuracy, tone: "good", text: (v) => pct(v), hint: "nas questões" },
};
function heatColor(v, scale, tone) {
  if (v == null) return null;
  const a = Math.max(0.1, Math.min(1, scale ? v / scale : v));
  return `color-mix(in srgb, var(--${tone}) ${(a * 100).toFixed(0)}%, var(--surface-2))`;
}

async function viewTrail(slug) {
  let d;
  try { d = await api(`/api/admin/trails/${encodeURIComponent(slug)}`); }
  catch (e) { if (e.status === 404) { setChildren(main, emptyState("Trilha não encontrada", h("p", {}, h("a", { href: "#/trails" }, "Voltar para as trilhas")))); return; } throw e; }
  const t = d.trail;
  let metric = "completion";
  const all = d.blocks.flatMap((b) => b.sections.flatMap((x) => x.items));
  const parts = [
    head(t.title, [t.description || "", t.active ? null : " (trilha desativada: os alunos não a veem)"], null, [h("a", { href: "#/trails" }, "Trilhas"), " / ", t.title]),
    h("section", { class: "grid kpis" }, kpi("Alunos", fmtInt(t.students), `${plural(t.active_7d, "ativo", "ativos")} em 7 dias`),
      kpi("Conclusão média", pct(t.avg_completion), plural(t.required_items, "item obrigatório", "itens obrigatórios")),
      kpi("Tempo por aluno", fmtTime(t.avg_seconds), `${fmtTime(t.seconds)} no total`), kpi("Visitas", fmtInt(t.visits)), kpi("Acerto", pct(t.accuracy))),
  ];
  if (!t.students) {
    setChildren(main, parts, emptyState("Ninguém começou esta trilha", h("p", {}, "Os números aparecem quando algum aluno abrir uma aula.")));
    return;
  }
  const heat = h("div"), legend = h("div", { class: "legend" });
  legend.style.marginTop = "12px";
  const seg = h("div", { class: "seg", role: "group", "aria-label": "Métrica do mapa" }, Object.entries(METRICS).map(([k, m]) =>
    h("button", { type: "button", "data-m": k, "aria-pressed": String(k === metric), onclick: () => { metric = k; drawHeat(); } }, m.label)));
  const drawHeat = () => {
    const m = METRICS[metric];
    const vals = all.map(m.get).filter((v) => v != null);
    const scale = metric === "time" ? Math.max(1, ...vals) : 0;
    setChildren(heat, d.blocks.map((b) => h("div", { class: "heat-block" },
      h("div", { class: "heat-title" }, h("h3", {}, b.title), h("span", { class: "muted" }, `conclusão média ${pct(b.avg_completion)} · abandono ${pct(b.abandon_rate)}`)),
      h("div", { class: "heat-sections" }, b.sections.map((sec) => h("div", { class: "heat-row" },
        h("span", { class: "heat-label", title: sec.title }, sec.title || "Itens"),
        h("div", { class: "heat-cells" }, sec.items.map((i) => {
          const v = m.get(i), bg = heatColor(v, scale, m.tone);
          const cell = h("span", { class: `cell ${bg ? "" : "empty"} ${i.optional ? "opt" : ""}`.trim(),
            "data-tip": `${i.title}\n${TYPE_LABEL[i.type] || i.type}${i.optional ? " · opcional" : ""}\n${m.label}: ${v == null ? "sem dados" : m.text(v)}\n${plural(i.students_opened, "aluno abriu", "alunos abriram")}` });
          if (bg) cell.style.background = bg;
          return cell;
        }))))))));
    const lo = heatColor(0.1, 0, m.tone), hi = heatColor(1, 0, m.tone);
    const gradient = h("i");
    gradient.style.background = `linear-gradient(90deg,${lo},${hi})`;
    const none = h("span", { class: "cell empty" });
    none.style.width = none.style.height = "14px";
    setChildren(legend, h("span", {}, "menos"), gradient, h("span", {}, `mais · ${m.label.toLowerCase()} (${m.hint})`), none, h("span", {}, "sem dados"));
    seg.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.m === metric)));
  };
  const heatCard = h("section", { class: "card" }, h("div", { class: "card-head" },
    h("div", {}, h("h2", {}, "Onde os alunos empacam"), h("span", { class: "muted" }, "cada quadrado é um item; passe o mouse para ver os números. Borda tracejada = opcional.")), seg), heat, legend);
  heatCard.style.marginBottom = "16px";
  const tables = d.blocks.map((b) => {
    const rows = [];
    for (const sec of b.sections) {
      rows.push(h("tr", { class: "group-row" }, h("td", { colspan: 6 }, sec.title || "Itens")));
      for (const i of sec.items) {
        rows.push(h("tr", {},
          h("td", {}, i.title, i.optional ? [" ", h("span", { class: "pill" }, "opcional")] : null, h("div", { class: "rank-sub" }, TYPE_LABEL[i.type] || i.type)),
          h("td", { class: "num" }, i.students_opened), h("td", { class: "num" }, i.students_opened ? fmtTime(i.avg_seconds) : "—"),
          h("td", {}, meter(i.abandon_rate, "warn")), h("td", {}, meter(i.completion)), h("td", {}, meter(i.accuracy, accKind(i.accuracy)))));
      }
    }
    const section = h("section", { class: "card" },
      h("div", { class: "card-head" }, h("h2", {}, b.title), h("span", { class: "muted" }, `${plural(b.students_opened, "aluno abriu", "alunos abriram")} · ${fmtTime(b.seconds)}`)),
      h("div", { class: "table-wrap" }, h("table", {}, h("thead", {}, h("tr", {}, h("th", { scope: "col" }, "Item"), h("th", { scope: "col", class: "num" }, "Abriram"),
        h("th", { scope: "col", class: "num" }, "Tempo médio"), h("th", { scope: "col" }, "Abandono"), h("th", { scope: "col" }, "Conclusão"), h("th", { scope: "col" }, "Acerto"))), h("tbody", {}, rows))));
    section.style.marginBottom = "16px";
    return section;
  });
  setChildren(main, parts, heatCard,
    h("section", { class: "grid cols-2" }, card("Questões mais erradas", "mín. 2 respostas", hardList(d.hardest_questions, false)), card("Aulas com mais abandono", "mín. 3 visitas", abandonItems(all))), tables);
  drawHeat();
}
function abandonItems(items) {
  const list = items.filter((i) => i.visits >= 3 && i.quick_visits).sort((a, b) => b.abandon_rate - a.abandon_rate || b.quick_visits - a.quick_visits).slice(0, 8);
  if (!list.length) return h("p", { class: "mini-empty" }, "Nenhum item com abandono relevante.");
  return h("ol", { class: "rank" }, list.map((i) => h("li", {}, h("div", { class: "rank-top" }, h("span", {}, i.title)), meter(i.abandon_rate, "warn"),
    h("span", { class: "rank-sub" }, `${i.quick_visits} de ${i.visits} visitas`))));
}

/* ---------- roteador e início ---------- */
async function route() {
  const my = ++token;
  redraw = [];
  const parts = (location.hash.replace(/^#\/?/, "") || "").split("/").filter(Boolean).map((p) => { try { return decodeURIComponent(p); } catch (e) { return p; } });
  const section = parts[0] || "overview";
  document.querySelectorAll("#nav a").forEach((a) => (a.dataset.nav === section ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current")));
  loading();
  try {
    if (section === "overview") await viewOverview();
    else if (section === "students") await (parts[1] ? viewStudent(parts[1]) : viewStudents());
    else if (section === "trails") await (parts[1] ? viewTrail(parts[1]) : viewTrails());
    else if (section === "import") viewImport();
    else setChildren(main, emptyState("Página não encontrada", h("p", {}, h("a", { href: "#/" }, "Voltar para a visão geral"))));
  } catch (err) {
    if (my !== token) return;
    if (err.status === 401 || err.status === 403) { location.replace("/"); return; }
    errorView(err);
  }
  if (my === token) { document.title = `${$("h1")?.textContent || "Administração"} · k_study`; window.scrollTo(0, 0); }
}
addEventListener("hashchange", route);

$("#logout-btn").addEventListener("click", async () => {
  try { await postJson("/api/auth/logout", {}); } catch (e) { /* sai mesmo assim */ }
  location.replace("/");
});

async function start() {
  paintThemeButton();
  try { await loadSession(); }
  catch (e) { $("#shell").hidden = false; errorView(e); return; }
  if (!session.user || !session.user.isAdmin) { location.replace("/"); return; }
  $("#user-name").textContent = session.user.name || "(sem nome)";
  $("#user-email").textContent = session.user.email;
  $("#shell").hidden = false;
  route();
}
start();
