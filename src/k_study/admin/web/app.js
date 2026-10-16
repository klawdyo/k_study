/* Painel do admin do k_study. Sem bibliotecas: gráficos em SVG escritos à mão. */
"use strict";

const $ = (sel, root = document) => root.querySelector(sel);
const main = $("#main");
const TYPE_LABEL = { video: "Vídeo", markdown: "Leitura", pdf: "PDF", link: "Link", questions: "Questões" };
let redraw = [];            // funções que redesenham os gráficos ao redimensionar
let token = 0;              // descarta respostas de rotas que já foram abandonadas

/* ---------- utilidades ---------- */
function esc(v) {
  return String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function fmtTime(s) {
  s = Math.round(s || 0);
  if (s < 60) return `${s} s`;
  if (s < 3600) { const m = Math.floor(s / 60), r = s % 60; return r ? `${m} min ${r} s` : `${m} min`; }
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60);
  return `${h} h ${String(m).padStart(2, "0")} min`;
}
function fmtHours(s) {            // total acumulado, para os cartões
  s = s || 0;
  if (s < 3600) return { v: String(Math.round(s / 60)), u: "min" };
  const h = s / 3600;
  return { v: h >= 100 ? String(Math.round(h)) : h.toFixed(1).replace(".", ","), u: "h" };
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

function meter(rate, kind) {
  if (rate == null) return `<span class="muted">—</span>`;
  const w = Math.max(0, Math.min(1, rate)) * 100;
  return `<div class="meter"><div class="meter-track"><div class="meter-fill ${kind || ""}" style="width:${w.toFixed(1)}%"></div></div>` +
         `<span class="meter-val">${pct(rate)}</span></div>`;
}
const accKind = (r) => (r == null ? "" : r >= 0.75 ? "good" : r >= 0.5 ? "warn" : "bad");

/* ---------- API ---------- */
class ApiError extends Error { constructor(status, code, message) { super(message); this.status = status; this.code = code; } }
async function api(path, opts) {
  let res;
  try { res = await fetch(path, opts); }
  catch (e) { throw new ApiError(0, "network", "Não foi possível falar com o servidor do painel. Ele ainda está rodando?"); }
  let data = null;
  try { data = await res.json(); } catch (e) { /* corpo vazio */ }
  if (!res.ok) throw new ApiError(res.status, data?.error || "error", data?.message || `Erro ${res.status}`);
  return data;
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

/* ---------- dica flutuante (tooltip) ---------- */
const tip = $("#tip");
document.addEventListener("pointermove", (e) => {
  const el = e.target.closest?.("[data-tip]");
  if (!el) { tip.hidden = true; return; }
  tip.innerHTML = el.dataset.tip;
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
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw);
  return { max: step * ticks, step };
}
function dayLabel(date) { const [, m, d] = date.split("-"); return `${d}/${m}`; }

/** Gráfico de colunas (tempo por dia). series: [{date, value}], unit: "time" */
function barChart(el, series, label) {
  const draw = () => {
    const W = Math.max(280, el.clientWidth), H = 220, L = 46, R = 8, T = 10, B = 26;
    const maxRaw = Math.max(...series.map((d) => d.value), 0);
    const useHours = maxRaw >= 7200, div = useHours ? 3600 : 60, unit = useHours ? "h" : "min";
    const { max, step } = niceMax(maxRaw / div);
    const iw = W - L - R, ih = H - T - B, bw = iw / series.length;
    let g = "";
    for (let v = 0; v <= max + 1e-9; v += step) {
      const y = T + ih - (v / max) * ih;
      g += `<line class="grid-line" x1="${L}" x2="${W - R}" y1="${y}" y2="${y}"/><text x="${L - 8}" y="${y + 4}" text-anchor="end">${(+v.toFixed(2)).toLocaleString("pt-BR")} ${unit}</text>`;
    }
    const every = W < 480 ? 7 : 5;
    series.forEach((d, i) => {
      const x = L + i * bw, h = max ? (d.value / div / max) * ih : 0;
      const tipTxt = `<b>${dayLabel(d.date)}</b><br>${fmtTime(d.value)} estudados<br>${plural(d.visits, "visita", "visitas")}`;
      g += `<g class="col" data-tip="${esc(tipTxt)}"><rect class="hit" x="${x}" y="${T}" width="${bw}" height="${ih}"/>` +
           (d.value ? `<rect class="bar" x="${x + bw * 0.14}" y="${T + ih - h}" width="${Math.max(2, bw * 0.72)}" height="${Math.max(2, h)}" rx="3"/>` : "") + `</g>`;
      if ((series.length - 1 - i) % every === 0) g += `<text x="${x + bw / 2}" y="${H - 6}" text-anchor="middle">${dayLabel(d.date)}</text>`;
    });
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}">${g}</svg>`;
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
    let g = "";
    for (let v = 0; v <= max + 1e-9; v += step) {
      const y = py(v);
      g += `<line class="grid-line" x1="${L}" x2="${W - R}" y1="${y}" y2="${y}"/><text x="${L - 8}" y="${y + 4}" text-anchor="end">${Math.round(v)}</text>`;
    }
    const pts = series.map((d, i) => `${px(i).toFixed(1)},${py(d.value).toFixed(1)}`);
    g += `<polygon class="area" points="${px(0)},${T + ih} ${pts.join(" ")} ${px(n - 1)},${T + ih}"/><polyline class="line" points="${pts.join(" ")}"/>`;
    const every = W < 480 ? 7 : 5;
    series.forEach((d, i) => {
      const tipTxt = `<b>${dayLabel(d.date)}</b><br>${plural(d.value, "aluno ativo", "alunos ativos")}`;
      const cw = iw / n;
      g += `<g class="col" data-tip="${esc(tipTxt)}"><rect class="hit" x="${px(i) - cw / 2}" y="${T}" width="${cw}" height="${ih}"/>` +
           (d.value ? `<circle class="dot" cx="${px(i)}" cy="${py(d.value)}" r="3.5"/>` : "") + `</g>`;
      if ((n - 1 - i) % every === 0) g += `<text x="${px(i)}" y="${H - 6}" text-anchor="middle">${dayLabel(d.date)}</text>`;
    });
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}">${g}</svg>`;
  };
  draw(); redraw.push(draw);
}
let resizeTimer;
addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => redraw.forEach((f) => f()), 120); });

/* ---------- tabela ordenável ---------- */
function sortableTable(container, { columns, rows, sortKey, sortDir = -1, rowHref, filter, emptyText }) {
  let state = { key: sortKey, dir: sortDir, text: "" };
  const render = () => {
    const col = columns.find((c) => c.key === state.key);
    let shown = rows.filter((r) => !state.text || filter(r).toLowerCase().includes(state.text));
    if (col) {
      shown = shown.slice().sort((a, b) => {
        const va = col.sort(a), vb = col.sort(b);
        const c = typeof va === "string" ? va.localeCompare(vb, "pt-BR") : va - vb;
        return c * state.dir || String(a.email ?? "").localeCompare(String(b.email ?? ""));
      });
    }
    const head = columns.map((c) => {
      const active = c.key === state.key;
      const arrow = active ? (state.dir > 0 ? "▲" : "▼") : "";
      return `<th scope="col" class="${c.num ? "num" : ""}" ${active ? `aria-sort="${state.dir > 0 ? "ascending" : "descending"}"` : ""}>` +
             `<button type="button" data-sort="${c.key}">${esc(c.label)}<span aria-hidden="true">${arrow}</span></button></th>`;
    }).join("");
    const body = shown.map((r) => {
      const href = rowHref ? rowHref(r) : "";
      return `<tr ${href ? `class="link" data-href="${esc(href)}"` : ""}>` +
        columns.map((c) => `<td class="${c.num ? "num" : ""} ${c.cls || ""}">${c.render(r)}</td>`).join("") + `</tr>`;
    }).join("");
    container.innerHTML = `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>` +
      (shown.length ? "" : `<p class="mini-empty">${esc(emptyText || "Nada encontrado.")}</p>`) +
      `<p class="table-note">${plural(shown.length, "linha", "linhas")}${state.text ? ` de ${fmtInt(rows.length)}` : ""}</p>`;
  };
  container.addEventListener("click", (e) => {
    const b = e.target.closest("[data-sort]");
    if (b) {
      const key = b.dataset.sort;
      state = { ...state, key, dir: state.key === key ? -state.dir : (columns.find((c) => c.key === key).num ? -1 : 1) };
      render(); container.querySelector(`[data-sort="${key}"]`)?.focus(); return;
    }
    const tr = e.target.closest("tr[data-href]");
    if (tr && !e.target.closest("a")) location.hash = tr.dataset.href;
  });
  render();
  return { setFilter(t) { state.text = t.trim().toLowerCase(); render(); } };
}

/* ---------- peças de tela ---------- */
const kpi = (label, value, note) =>
  `<div class="card kpi"><span class="kpi-label">${esc(label)}</span><span class="kpi-value">${value}</span>${note ? `<span class="kpi-note">${esc(note)}</span>` : ""}</div>`;
const loading = () => { main.innerHTML = `<div class="grid kpis"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div>`; };
function emptyState(title, text) { return `<div class="card empty"><h2>${esc(title)}</h2>${text}</div>`; }
function errorView(err) {
  if (err.code === "database_missing" || err.code === "database_error") {
    main.innerHTML = emptyState("O banco de dados ainda não está pronto",
      `<p>${esc(err.message)}</p><p>Depois que o banco existir, recarregue esta página.</p><p><button class="btn" id="retry">Tentar de novo</button></p>`);
  } else {
    main.innerHTML = emptyState("Algo deu errado", `<p>${esc(err.message)}</p><p><button class="btn" id="retry">Tentar de novo</button></p>`);
  }
  $("#retry")?.addEventListener("click", route);
}
const itemLink = (slug) => `#/trails/${encodeURIComponent(slug)}`;

/* ---------- telas ---------- */
async function viewOverview() {
  const d = await api("/api/admin/overview");
  const t = d.totals, hrs = fmtHours(t.seconds);
  if (!t.students) {
    main.innerHTML = head("Visão geral", "Estatísticas de estudo de todos os alunos.") +
      emptyState("Nenhum aluno ainda", `<p>Assim que alguém abrir o servidor dos alunos (<code>kstudy serve</code>) e informar o e-mail, as estatísticas aparecem aqui.</p>` +
        `<p>${plural(t.trails, "trilha disponível", "trilhas disponíveis")} para estudar.</p>`);
    return;
  }
  const quickRate = t.visits ? t.quick_visits / t.visits : null;
  main.innerHTML = head("Visão geral", `Atualizado ${fmtWhen(d.generated_at)}. Datas em UTC.`, `<button class="btn" id="refresh">Atualizar</button>`) +
    `<section class="grid kpis" aria-label="Resumo">` +
    kpi("Alunos", fmtInt(t.students), "cadastrados") +
    kpi("Ativos em 7 dias", `${fmtInt(t.active_7d)}`, t.students ? `${pct(t.active_7d / t.students)} dos alunos` : "") +
    kpi("Tempo estudado", `${hrs.v}<small> ${hrs.u}</small>`, `${fmtTime(t.students ? t.seconds / t.students : 0)} por aluno`) +
    kpi("Visitas", fmtInt(t.visits), quickRate == null ? "" : `${pct(quickRate)} só abriram e saíram`) +
    kpi("Trilhas", fmtInt(t.trails), t.answers ? `${pct(t.accuracy)} de acerto em ${fmtInt(t.answers)} respostas` : "Sem respostas ainda") +
    `</section>` +
    `<section class="grid cols-2"><div class="card"><div class="card-head"><h2>Tempo estudado por dia</h2><span class="muted">últimos 30 dias</span></div><div class="chart" id="ch-time"></div></div>` +
    `<div class="card"><div class="card-head"><h2>Alunos ativos por dia</h2><span class="muted">últimos 30 dias</span></div><div class="chart" id="ch-active"></div></div></section>` +
    `<section class="grid cols-3">` +
    `<div class="card"><div class="card-head"><h2>Conclusão por trilha</h2><span class="muted">só quem iniciou</span></div>${trailRank(d.trails)}</div>` +
    `<div class="card"><div class="card-head"><h2>Questões mais erradas</h2><span class="muted">mín. 2 respostas</span></div>${hardList(d.hardest_questions, true)}</div>` +
    `<div class="card"><div class="card-head"><h2>Aulas com mais abandono</h2><span class="muted">visitas &lt; 10 s</span></div>${abandonList(d.abandoned_items)}</div>` +
    `</section>` +
    `<section class="card"><div class="card-head"><h2>Atividade recente</h2></div>${recentFeed(d.recent)}</section>`;
  barChart($("#ch-time"), d.daily.map((x) => ({ date: x.date, value: x.seconds, visits: x.visits })), "Tempo estudado por dia nos últimos 30 dias");
  lineChart($("#ch-active"), d.daily.map((x) => ({ date: x.date, value: x.active_students })), "Alunos ativos por dia nos últimos 30 dias");
  $("#refresh").addEventListener("click", route);
}
function head(title, sub, tools = "", crumbs = "") {
  return `<div class="page-head"><div>${crumbs ? `<div class="crumbs">${crumbs}</div>` : ""}<h1>${esc(title)}</h1>${sub ? `<p>${sub}</p>` : ""}</div>${tools ? `<div>${tools}</div>` : ""}</div>`;
}
function trailRank(list) {
  if (!list.length) return `<p class="mini-empty">Nenhuma trilha indexada ainda. Rode <code>kstudy sync</code>.</p>`;
  return `<ol class="rank">${list.map((t) => `<li><div class="rank-top"><a href="${itemLink(t.slug)}">${esc(t.title)}</a></div>` +
    `${meter(t.avg_completion, "")}<span class="rank-sub">${plural(t.students, "aluno iniciou", "alunos iniciaram")}</span></li>`).join("")}</ol>`;
}
function hardList(list, showTrail) {
  if (!list.length) return `<p class="mini-empty">Ainda não há erros suficientes para listar.</p>`;
  return `<ol class="rank">${list.map((q) => `<li><div class="rank-top"><span>${esc(q.item_title)} · ${esc(q.question_id)}</span></div>` +
    `${meter(q.error_rate, "bad")}<span class="rank-sub">${showTrail ? esc(q.trail_title) + " · " : ""}${q.wrong} erros em ${q.answers} respostas</span></li>`).join("")}</ol>`;
}
function abandonList(list) {
  if (!list.length) return `<p class="mini-empty">Nenhuma aula com abandono relevante (precisa de 3 visitas ou mais).</p>`;
  return `<ol class="rank">${list.map((a) => `<li><div class="rank-top"><a href="${itemLink(a.trail)}">${esc(a.title)}</a></div>` +
    `${meter(a.abandon_rate, "warn")}<span class="rank-sub">${esc(a.trail_title)} · ${a.quick_visits} de ${a.visits} visitas</span></li>`).join("")}</ol>`;
}
function recentFeed(list) {
  if (!list.length) return `<p class="mini-empty">Nenhuma atividade registrada.</p>`;
  const verb = { visit: (e) => `abriu <b>${esc(e.title)}</b> (${esc(e.detail)})`, answer: (e) => `${e.detail} uma questão de <b>${esc(e.title)}</b>`, done: (e) => `concluiu <b>${esc(e.title)}</b>` };
  return `<ul class="feed">${list.map((e) => `<li><span class="dot-kind ${e.kind}" aria-hidden="true"></span>` +
    `<span class="what"><a href="#/students/${e.student_id}">${esc(e.email)}</a> ${verb[e.kind](e)} <span class="muted">· ${esc(e.trail_title)}</span></span>` +
    `<span class="when">${fmtWhen(e.at)}</span></li>`).join("")}</ul>`;
}

async function viewStudents() {
  const { students } = await api("/api/admin/students");
  if (!students.length) {
    main.innerHTML = head("Alunos", "Quem já entrou para estudar.") +
      emptyState("Nenhum aluno cadastrado", `<p>Os alunos aparecem aqui depois de informarem o e-mail na interface de estudo.</p>`);
    return;
  }
  main.innerHTML = head("Alunos", `${plural(students.length, "aluno cadastrado", "alunos cadastrados")}.`) +
    `<div class="card"><div class="toolbar"><input type="search" id="filter" placeholder="Filtrar por e-mail" aria-label="Filtrar alunos por e-mail"></div><div id="table"></div></div>`;
  const t = sortableTable($("#table"), {
    rows: students, sortKey: "last", sortDir: -1, filter: (r) => r.email, rowHref: (r) => `#/students/${r.id}`, emptyText: "Nenhum aluno com esse e-mail.",
    columns: [
      { key: "email", label: "E-mail", sort: (r) => r.email, render: (r) => `<a class="email" href="#/students/${r.id}">${esc(r.email)}</a>` },
      { key: "created", label: "Cadastro", sort: (r) => r.created_at || "", render: (r) => fmtDate(r.created_at), cls: "small" },
      { key: "last", label: "Última atividade", sort: (r) => r.last_activity || "", render: (r) => esc(fmtWhen(r.last_activity)), cls: "small" },
      { key: "time", label: "Tempo", num: true, sort: (r) => r.seconds, render: (r) => fmtTime(r.seconds) },
      { key: "done", label: "Itens feitos", num: true, sort: (r) => r.items_done, render: (r) => fmtInt(r.items_done) },
      { key: "acc", label: "Acerto", num: true, sort: (r) => num(r.accuracy), render: (r) => (r.answers ? `<span class="pill ${accKind(r.accuracy)}">${pct(r.accuracy)}</span> <span class="muted">${r.correct}/${r.answers}</span>` : `<span class="muted">—</span>`) },
    ],
  });
  $("#filter").addEventListener("input", (e) => t.setFilter(e.target.value));
}

async function viewStudent(id) {
  let d;
  try { d = await api(`/api/admin/students/${id}`); }
  catch (e) { if (e.status === 404) { main.innerHTML = emptyState("Aluno não encontrado", `<p><a href="#/students">Voltar para a lista de alunos</a></p>`); return; } throw e; }
  const s = d.student, quick = s.visits ? s.quick_visits / s.visits : null;
  const crumbs = `<a href="#/students">Alunos</a> / ${esc(s.email)}`;
  let html = head(s.email, `Cadastrado em ${fmtDate(s.created_at)} · última atividade ${esc(fmtWhen(s.last_activity))}`, "", crumbs) +
    `<section class="grid kpis">` + kpi("Tempo estudado", fmtTime(s.seconds)) + kpi("Visitas", fmtInt(s.visits)) +
    kpi("Só abriu e saiu", fmtInt(s.quick_visits), quick == null ? "" : `${pct(quick)} das visitas`) +
    kpi("Itens feitos", fmtInt(s.items_done)) +
    kpi("Acerto", s.answers ? pct(s.accuracy) : "—", s.answers ? `${s.correct} de ${s.answers} respostas` : "Sem respostas") + `</section>`;
  if (!d.trails.length) html += emptyState("Sem atividade em trilhas", `<p>Este aluno ainda não abriu nenhuma aula.</p>`);
  for (const tr of d.trails) html += studentTrail(tr);
  main.innerHTML = html;
}
function studentTrail(tr) {
  const maxSec = Math.max(1, ...tr.items.map((i) => i.seconds));
  let lastBlock = null, rows = "";
  for (const i of tr.items) {
    if (i.block_id !== lastBlock) { lastBlock = i.block_id; rows += `<tr class="group-row"><td colspan="6">${esc(i.block_title)}</td></tr>`; }
    const qs = i.questions.length ? `<span class="qs">${i.questions.map((q) => `<span class="q ${q.correct ? "" : "wrong"}" data-tip="${esc(`<b>${q.question_id}</b><br>${q.correct ? "Acertou" : "Errou"} · marcou ${q.chosen.join(", ") || "—"}`)}"></span>`).join("")}</span> <span class="muted">${i.questions.filter((q) => q.correct).length}/${i.questions.length}</span>` : `<span class="muted">—</span>`;
    rows += `<tr><td>${esc(i.title)}${i.optional ? ` <span class="pill">opcional</span>` : ""}<div class="rank-sub">${esc(TYPE_LABEL[i.type] || i.type)} · ${esc(i.section || "")}</div></td>` +
      `<td>${i.done ? `<span class="pill good">feito</span>` : `<span class="pill">pendente</span>`}</td>` +
      `<td class="num"><div class="meter"><div class="meter-track"><div class="meter-fill" style="width:${(i.seconds / maxSec * 100).toFixed(1)}%"></div></div><span class="meter-val" style="min-width:5.5em">${i.seconds ? fmtTime(i.seconds) : "—"}</span></div></td>` +
      `<td class="num">${i.visits || "—"}</td><td class="num">${i.quick_visits ? `<span class="pill warn">${i.quick_visits}</span>` : "—"}</td><td>${qs}</td></tr>`;
  }
  return `<section class="card" style="margin-bottom:16px"><div class="card-head"><h2><a href="${itemLink(tr.slug)}">${esc(tr.title)}</a></h2>` +
    `<span class="muted">${tr.required_done} de ${tr.required_items} itens obrigatórios · ${fmtTime(tr.seconds)}${tr.answers ? ` · acerto ${pct(tr.accuracy)}` : ""}</span></div>` +
    `<div class="meter tall" style="margin-bottom:14px"><div class="meter-track"><div class="meter-fill good" style="width:${((tr.completion || 0) * 100).toFixed(1)}%"></div></div><span class="meter-val">${pct(tr.completion)}</span></div>` +
    `<div class="table-wrap"><table><thead><tr><th scope="col">Item</th><th scope="col">Estado</th><th scope="col" class="num">Tempo</th><th scope="col" class="num">Visitas</th>` +
    `<th scope="col" class="num">Só abriu e saiu</th><th scope="col">Questões</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
}

async function viewTrails() {
  const { trails } = await api("/api/admin/trails");
  if (!trails.length) {
    main.innerHTML = head("Trilhas", "Os cursos disponíveis para os alunos.") +
      emptyState("Nenhuma trilha indexada", `<p>Crie uma trilha em <code>content/</code> e rode <code>kstudy sync</code>.</p>`);
    return;
  }
  main.innerHTML = head("Trilhas", `${plural(trails.length, "trilha", "trilhas")} no catálogo.`) +
    `<div class="grid cols-2">${trails.map((t) => `<a class="card trail-card" href="${itemLink(t.slug)}"><div><h3>${esc(t.title)}</h3>` +
      `${t.description ? `<p class="muted" style="margin:4px 0 0">${esc(t.description)}</p>` : ""}</div>${meter(t.avg_completion)}` +
      `<div class="trail-meta"><span>${plural(t.students, "aluno", "alunos")}</span><span>${plural(t.blocks, "bloco", "blocos")} · ${plural(t.items, "item", "itens")}</span>` +
      `<span>${fmtTime(t.avg_seconds)} por aluno</span><span>${t.accuracy == null ? "sem respostas" : `acerto ${pct(t.accuracy)}`}</span></div></a>`).join("")}</div>`;
}

const METRICS = {
  completion: { label: "Conclusão", get: (i) => i.completion, tone: "accent", text: (v) => pct(v), hint: "alunos que concluíram" },
  abandon: { label: "Abandono", get: (i) => i.abandon_rate, tone: "warn", text: (v) => pct(v), hint: "visitas &lt; 10 s" },
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
  catch (e) { if (e.status === 404) { main.innerHTML = emptyState("Trilha não encontrada", `<p><a href="#/trails">Voltar para as trilhas</a></p>`); return; } throw e; }
  const t = d.trail;
  let metric = "completion";
  const crumbs = `<a href="#/trails">Trilhas</a> / ${esc(t.title)}`;
  const all = d.blocks.flatMap((b) => b.sections.flatMap((s) => s.items));
  main.innerHTML = head(t.title, t.description ? esc(t.description) : "", "", crumbs) +
    `<section class="grid kpis">` + kpi("Alunos", fmtInt(t.students), `${plural(t.active_7d, "ativo", "ativos")} em 7 dias`) +
    kpi("Conclusão média", pct(t.avg_completion), `${plural(t.required_items, "item obrigatório", "itens obrigatórios")}`) +
    kpi("Tempo por aluno", fmtTime(t.avg_seconds), `${fmtTime(t.seconds)} no total`) + kpi("Visitas", fmtInt(t.visits)) +
    kpi("Acerto", pct(t.accuracy)) + `</section>`;
  if (!t.students) { main.insertAdjacentHTML("beforeend", emptyState("Ninguém começou esta trilha", `<p>Os números aparecem quando algum aluno abrir uma aula.</p>`)); return; }
  main.insertAdjacentHTML("beforeend",
    `<section class="card" style="margin-bottom:16px"><div class="card-head"><div><h2>Onde os alunos empacam</h2><span class="muted">cada quadrado é um item; passe o mouse para ver os números. Borda tracejada = opcional.</span></div>` +
    `<div class="seg" id="metric" role="group" aria-label="Métrica do mapa">${Object.entries(METRICS).map(([k, m]) => `<button type="button" data-m="${k}" aria-pressed="${k === metric}">${m.label}</button>`).join("")}</div></div>` +
    `<div id="heat"></div><div class="legend" id="legend" style="margin-top:12px"></div></section>`);
  const drawHeat = () => {
    const m = METRICS[metric];
    const vals = all.map(m.get).filter((v) => v != null);
    const scale = metric === "time" ? Math.max(1, ...vals) : 0;
    $("#heat").innerHTML = d.blocks.map((b) => `<div class="heat-block"><div class="heat-title"><h3>${esc(b.title)}</h3>` +
      `<span class="muted">conclusão média ${pct(b.avg_completion)} · abandono ${pct(b.abandon_rate)}</span></div><div class="heat-sections">` +
      b.sections.map((s) => `<div class="heat-row"><span class="heat-label" title="${esc(s.title)}">${esc(s.title || "Itens")}</span><div class="heat-cells">` +
        s.items.map((i) => {
          const v = m.get(i), bg = heatColor(v, scale, m.tone);
          const tipTxt = `<b>${esc(i.title)}</b><br>${esc(TYPE_LABEL[i.type] || i.type)}${i.optional ? " · opcional" : ""}<br>${m.label}: ${v == null ? "sem dados" : m.text(v)}<br>${plural(i.students_opened, "aluno abriu", "alunos abriram")}`;
          return `<span class="cell ${bg ? "" : "empty"} ${i.optional ? "opt" : ""}" ${bg ? `style="background:${bg}"` : ""} data-tip="${esc(tipTxt)}"></span>`;
        }).join("") + `</div></div>`).join("") + `</div></div>`).join("");
    const lo = heatColor(0.1, 0, m.tone), hi = heatColor(1, 0, m.tone);
    $("#legend").innerHTML = `<span>menos</span><i style="background:linear-gradient(90deg,${lo},${hi})"></i><span>mais · ${m.label.toLowerCase()} (${m.hint})</span><span class="cell empty" style="width:14px;height:14px"></span><span>sem dados</span>`;
    document.querySelectorAll("#metric button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.m === metric)));
  };
  $("#metric").addEventListener("click", (e) => { const b = e.target.closest("[data-m]"); if (b) { metric = b.dataset.m; drawHeat(); } });
  drawHeat();
  main.insertAdjacentHTML("beforeend", `<section class="grid cols-2" id="hardrow"></section>`);
  $("#hardrow").innerHTML =
    `<div class="card"><div class="card-head"><h2>Questões mais erradas</h2><span class="muted">mín. 2 respostas</span></div>${hardList(d.hardest_questions, false)}</div>` +
    `<div class="card"><div class="card-head"><h2>Aulas com mais abandono</h2><span class="muted">mín. 3 visitas</span></div>${abandonItems(all)}</div>`;
  let tables = "";
  for (const b of d.blocks) {
    let rows = "";
    for (const s of b.sections) {
      rows += `<tr class="group-row"><td colspan="7">${esc(s.title || "Itens")}</td></tr>`;
      for (const i of s.items) {
        rows += `<tr><td>${esc(i.title)}${i.optional ? ` <span class="pill">opcional</span>` : ""}<div class="rank-sub">${esc(TYPE_LABEL[i.type] || i.type)}</div></td>` +
          `<td class="num">${i.students_opened}</td><td class="num">${i.students_opened ? fmtTime(i.avg_seconds) : "—"}</td>` +
          `<td>${meter(i.abandon_rate, "warn")}</td><td>${meter(i.completion)}</td><td>${meter(i.accuracy, accKind(i.accuracy))}</td></tr>`;
      }
    }
    tables += `<section class="card" style="margin-bottom:16px"><div class="card-head"><h2>${esc(b.title)}</h2><span class="muted">${plural(b.students_opened, "aluno abriu", "alunos abriram")} · ${fmtTime(b.seconds)}</span></div>` +
      `<div class="table-wrap"><table><thead><tr><th scope="col">Item</th><th scope="col" class="num">Abriram</th><th scope="col" class="num">Tempo médio</th>` +
      `<th scope="col">Abandono</th><th scope="col">Conclusão</th><th scope="col">Acerto</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
  }
  main.insertAdjacentHTML("beforeend", tables);
}
function abandonItems(items) {
  const list = items.filter((i) => i.visits >= 3 && i.quick_visits).sort((a, b) => b.abandon_rate - a.abandon_rate || b.quick_visits - a.quick_visits).slice(0, 8);
  if (!list.length) return `<p class="mini-empty">Nenhum item com abandono relevante.</p>`;
  return `<ol class="rank">${list.map((i) => `<li><div class="rank-top"><span>${esc(i.title)}</span></div>${meter(i.abandon_rate, "warn")}<span class="rank-sub">${i.quick_visits} de ${i.visits} visitas</span></li>`).join("")}</ol>`;
}

/* ---------- roteador e início ---------- */
async function route() {
  const my = ++token;
  redraw = [];
  const parts = (location.hash.replace(/^#\/?/, "") || "").split("/").filter(Boolean).map(decodeURIComponent);
  const section = parts[0] || "overview";
  document.querySelectorAll("#nav a").forEach((a) => (a.dataset.nav === section ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current")));
  loading();
  try {
    if (section === "overview") await viewOverview();
    else if (section === "students") await (parts[1] ? viewStudent(parts[1]) : viewStudents());
    else if (section === "trails") await (parts[1] ? viewTrail(parts[1]) : viewTrails());
    else main.innerHTML = emptyState("Página não encontrada", `<p><a href="#/">Voltar para a visão geral</a></p>`);
  } catch (err) {
    if (my !== token) return;
    if (err.code === "login_required") return start();
    errorView(err);
  }
  if (my === token) { document.title = `${$("h1")?.textContent || "Painel"} · k_study`; window.scrollTo(0, 0); }
}
addEventListener("hashchange", route);

async function start() {
  paintThemeButton();
  let session;
  try { session = await api("/api/admin/session"); }
  catch (e) { $("#shell").hidden = false; errorView(e); return; }
  const need = session.required && !session.authenticated;
  $("#login").hidden = !need;
  $("#shell").hidden = need;
  $("#logout-btn").hidden = !session.required;
  if (need) { $("#login-pass").focus(); return; }
  route();
}
$("#login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const err = $("#login-error");
  err.hidden = true;
  try {
    await api("/api/admin/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password: $("#login-pass").value }) });
    $("#login-pass").value = "";
    start();
  } catch (ex) { err.textContent = ex.message; err.hidden = false; }
});
$("#logout-btn").addEventListener("click", async () => {
  try { await api("/api/admin/logout", { method: "POST" }); } catch (e) { /* ignora */ }
  start();
});
start();
