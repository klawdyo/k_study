"use strict";
/* Web UI. It keeps no state of its own: content and progress come from and go to the API only.
   Identifiers are in English; the text shown to the user is in Portuguese. */

const $ = (selector, root = document) => root.querySelector(selector);
const h = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (value !== false && value != null) node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) if (child != null) node.append(child.nodeType ? child : document.createTextNode(child));
  return node;
};

const KINDS = {
  video:     { icon: "smart_display", label: "Vídeo" },
  markdown:  { icon: "article", label: "Leitura" },
  pdf:       { icon: "picture_as_pdf", label: "PDF" },
  link:      { icon: "link", label: "Matéria" },
  questions: { icon: "quiz", label: "Questões" },
};

/* Icons: Material Design (outlined), served from vendor/icons */
const ICON_NAMES = ["smart_display", "article", "picture_as_pdf", "link", "quiz", "check_circle_filled", "radio_button_unchecked", "menu", "open_in_new"];
const SVG = {};
async function loadIcons() {
  await Promise.all(ICON_NAMES.map(async (name) => { try { SVG[name] = await getText(`vendor/icons/${name}.svg`); } catch { SVG[name] = ""; } }));
}
const icon = (name, cls = "") => h("span", { class: "ic " + cls, "aria-hidden": "true", html: SVG[name] || "" });

const state = {
  config: null,
  block: null, blockUrl: null, items: [],        // flattened items; each has .section and .key
  progress: { items: {}, answers: {}, notes: {} },  // mirror of what the API returned
  current: null,
  setup: null,                                     // {configured, dataDir, source, ...} from /api/setup
};

/* ---------- API ---------- */
async function getJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${response.status} ao carregar ${url}`);
  return response.json();
}
async function getText(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${response.status} ao carregar ${url}`);
  return response.text();
}
const contentUrl = (path) => new URL("/api/content/" + path, location.origin).href;
const resolve = (path, base) => new URL(path, base).href;
const keyPath = (key) => key.split("/").map(encodeURIComponent).join("/");

/* Every progress change goes through here; the API saves the file and returns the full state. */
async function mutate(method, path, body) {
  try {
    const response = await fetch("/api/progress/" + path, {
      method, headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
    if (!response.ok) throw new Error(String(response.status));
    state.progress = await response.json();
    banner(null);
  } catch (error) {
    banner("Não consegui gravar na API (" + error.message + "). Confira se o servidor está rodando; nada foi salvo.");
    await reloadProgress();
  }
}
async function reloadProgress() {
  try { state.progress = await getJson("/api/progress"); banner(null); return true; }
  catch { banner("A API não respondeu. Inicie o servidor: study serve"); return false; }
}
function banner(message) {
  let node = $("#banner");
  if (!message) { if (node) node.remove(); return; }
  if (!node) { node = h("div", { id: "banner", class: "banner" }); document.body.prepend(node); }
  node.textContent = message;
}

// When the tab gets focus again, re-read the state from the API (the single source of truth).
let syncing = false;
async function sync() {
  if (!state.block || syncing) return;
  syncing = true;
  const before = JSON.stringify(state.progress);
  if (await reloadProgress() && JSON.stringify(state.progress) !== before) {
    drawMenu();
    const typing = document.activeElement && document.activeElement.tagName === "TEXTAREA";
    if (state.current && !typing) openItem(state.current, false);
  }
  syncing = false;
}
document.addEventListener("visibilitychange", () => { if (!document.hidden) sync(); });
window.addEventListener("focus", sync);

/* ---------- block ---------- */
function flatten(block) {
  const out = [];
  for (const section of block.sections) for (const item of section.items) {
    out.push(Object.assign({}, item, { section, key: `${block.id}/${item.id}` }));
  }
  return out;
}
const isDone = (item) => !!state.progress.items[item.key]?.done;
const nextItem = () => state.items.find((i) => !isDone(i) && !i.optional);

async function openBlock(id) {
  const entry = state.config.blocks.find((b) => b.id === id) || state.config.blocks[0];
  state.blockUrl = contentUrl(entry.file);
  state.block = await getJson(state.blockUrl);
  state.items = flatten(state.block);
  $("#block-select").value = entry.id;
  drawMenu();
  const target = location.hash.slice(1).split("/");
  const item = target[0] === state.block.id && state.items.find((i) => i.id === target[1]);
  openItem(item || nextItem() || state.items[0], false);
}

/* ---------- sidebar ---------- */
function drawMenu() {
  const nav = $("#sidebar");
  nav.replaceChildren();
  const next = nextItem();
  for (const section of state.block.sections) {
    const done = section.items.filter((i) => isDone({ key: `${state.block.id}/${i.id}` })).length;
    const box = h("div", { class: "section" + (section._collapsed ? " collapsed" : "") });
    box.append(h("h3", { onclick: () => { section._collapsed = !section._collapsed; box.classList.toggle("collapsed"); } },
      h("span", {}, section.title), h("span", { title: counterTitle(section.items.map((i) => ({ key: `${state.block.id}/${i.id}`, optional: i.optional }))) }, `${done}/${section.items.length}`)));
    const list = h("div", { class: "items" });
    for (const raw of section.items) {
      const item = state.items.find((x) => x.id === raw.id);
      const kind = KINDS[raw.type] || { icon: "article", label: raw.type };
      list.append(h("button", {
        class: "item" + (isDone(item) ? " done" : "") + (next && next.id === raw.id ? " next" : "") + (state.current && state.current.id === raw.id ? " active" : ""),
        "data-id": raw.id,
        onclick: () => { openItem(item); document.body.classList.remove("menu-open"); },
      },
        icon(isDone(item) ? "check_circle_filled" : "radio_button_unchecked", "status"),
        h("span", {}, h("span", { class: "title" }, icon(kind.icon, "kind"), raw.title,
          next && next.id === raw.id ? h("span", { class: "tag-next" }, "PRÓXIMO") : null),
          h("span", { class: "meta" }, [kind.label, raw.optional ? "opcional" : null, raw.duration, raw.channel].filter(Boolean).join(" · ")))));
    }
    box.append(list);
    nav.append(box);
  }
  if (state.setup && state.setup.source !== "flag" && state.setup.source !== "env") {
    nav.append(h("div", { class: "section" },
      h("button", { class: "btn small-btn", onclick: () => showSetup("Escolha a nova pasta de dados.") }, "Trocar a pasta de dados"),
      h("p", { class: "muted small", title: state.setup.dataDir }, "Pasta atual: " + state.setup.dataDir)));
  }
  const total = state.items.length, finished = state.items.filter(isDone).length;
  $("#overall-fill").style.width = total ? `${(100 * finished) / total}%` : "0";
  $("#overall-text").textContent = `${finished}/${total}`;
  $(".overall").title = counterTitle(state.items);
}
// "4 de 8 itens feitos (3 de 7 obrigatórios; 1 de 1 opcional)": every item that is done counts.
function counterTitle(items) {
  const done = items.filter(isDone).length;
  const required = items.filter((i) => !i.optional), optional = items.filter((i) => i.optional);
  const parts = [`${required.filter(isDone).length} de ${required.length} obrigatórios`];
  if (optional.length) parts.push(`${optional.filter(isDone).length} de ${optional.length} opcionais`);
  return `${done} de ${items.length} itens feitos (${parts.join("; ")}). Os opcionais não bloqueiam o "PRÓXIMO".`;
}

/* ---------- items ---------- */
async function openItem(item, byClick = true) {
  if (!item) { $("#main").replaceChildren(h("p", {}, "Bloco vazio.")); return; }
  state.current = item;
  if (byClick) history.replaceState(null, "", `#${state.block.id}/${item.id}`);
  // opening an item by click marks it as done (it can be unmarked on the page)
  if (byClick && !isDone(item)) await mutate("PUT", `items/${keyPath(item.key)}`, { done: true });
  drawMenu();
  const main = $("#main");
  const kind = KINDS[item.type] || { icon: "article", label: item.type };
  const badges = h("div", { class: "badges" }, h("span", { class: "badge" }, kind.label));
  if (item.duration) badges.append(h("span", { class: "badge" }, item.duration));
  if (item.channel) badges.append(h("span", { class: "badge" }, item.channel));
  if (item.optional) badges.append(h("span", { class: "badge" }, "opcional"));
  if (item.type === "video" && item.review) badges.append(h("span", { class: "badge ok", title: "Li a transcrição e comparei com os tópicos dos slides; os detalhes estão em \"Conferência com os slides\", abaixo do vídeo." }, item.review.badge));
  if (item.type === "video" && !item.review) badges.append(h("span", { class: "badge warn", title: "Ainda não li a transcrição deste vídeo para comparar com os slides." }, "transcrição ainda não lida"));

  const body = h("div");
  main.replaceChildren(...[
    h("p", { class: "crumb" }, `${state.block.title} › ${item.section.title}`),
    h("h1", { class: "page-title" }, item.title),
    badges,
    item.type === "video" && !item.review
      ? h("p", { class: "muted small" }, "Ainda não li a transcrição deste vídeo para checar se ele explica o que está nos slides. Se algo não bater com o slide da professora, vale o slide.") : null,
    item.note ? h("div", { class: "goals" }, h("strong", {}, "Nota"), h("p", { html: marked.parseInline(item.note) })) : null,
    item.goals?.length ? h("div", { class: "goals" }, h("strong", {}, item.goalsTitle || "O que você deve sair sabendo"), h("ul", {}, item.goals.map((g) => h("li", { html: marked.parseInline(g) })))) : null,
    item.warnings?.length ? h("div", { class: "goals warn" }, h("strong", {}, "Atenção: este vídeo diverge dos slides"), h("ul", {}, item.warnings.map((w) => h("li", { html: marked.parseInline(w) })))) : null,
    body,
  ].filter(Boolean));
  try { await renderItem(item, body); }
  catch (error) { body.append(h("div", { class: "verdict no" }, `Erro ao carregar este item: ${error.message}`)); }

  if (state.current !== item) return;
  const doneButton = h("button", { class: "btn done-btn" + (isDone(item) ? " done" : ""), onclick: () => toggleDone(item) });
  doneButton.id = "done-btn";
  setDoneLabel(doneButton, isDone(item));
  const following = state.items[state.items.findIndex((x) => x.key === item.key) + 1];
  const actions = h("div", { class: "actions" }, doneButton,
    following ? h("button", { class: "btn primary", onclick: () => openItem(following) }, "Próximo item →") : null);
  const notes = h("textarea", { class: "notes", placeholder: "Anotações suas sobre este item (dúvidas, o que errou, o que reler)…" });
  notes.value = state.progress.notes[item.key] || "";
  let timer;
  notes.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(() => mutate("PUT", `notes/${keyPath(item.key)}`, { text: notes.value }), 500); });
  main.append(actions, h("label", { class: "notes-label" }, "Anotações"), notes);
  if (byClick) window.scrollTo(0, 0);
}

async function toggleDone(item, value) {
  const next = value === undefined ? !isDone(item) : value;
  await mutate("PUT", `items/${keyPath(item.key)}`, { done: next });
  drawMenu();
  const button = $("#done-btn");
  if (button && state.current && state.current.key === item.key) { button.className = "btn done-btn" + (isDone(item) ? " done" : ""); setDoneLabel(button, isDone(item)); }
}
function setDoneLabel(button, done) {
  button.replaceChildren(icon(done ? "check_circle_filled" : "radio_button_unchecked"), done ? "Feito · clique para desmarcar" : "Marcar como feito");
}

async function renderItem(item, body) {
  if (item.type === "video") return renderVideo(item, body);
  if (item.type === "markdown") {
    let text, base;
    if (item.content != null) { text = item.content; base = state.blockUrl; }
    else { base = resolve(item.path, state.blockUrl); text = await getText(base); }
    return renderMarkdown(text, base, body);
  }
  if (item.type === "pdf") {
    const url = resolve(item.path, state.blockUrl);
    body.append(h("div", { class: "pdf-wrap" }, h("iframe", { src: url, title: item.title })),
      h("p", {}, h("a", { class: "btn", href: url, target: "_blank", rel: "noopener" }, icon("open_in_new"), "Abrir o PDF em outra aba")));
    return;
  }
  if (item.type === "link") {
    if (item.description) body.append(h("div", { class: "md", html: marked.parse(item.description) }));
    body.append(h("div", { class: "link-card" }, h("p", {}, item.url),
      h("a", { class: "btn primary", href: item.url, target: "_blank", rel: "noopener" }, icon("open_in_new"), "Abrir a matéria em outra aba")));
    return;
  }
  if (item.type === "questions") return renderQuestions(item, body);
  body.append(h("p", {}, `Tipo de item desconhecido: ${item.type}`));
}

/* ---------- markdown ---------- */
function renderMarkdown(text, baseUrl, target) {
  const box = h("div", { class: "md", html: marked.parse(text) });
  for (const image of box.querySelectorAll("img")) image.src = resolve(image.getAttribute("src"), baseUrl);
  for (const link of box.querySelectorAll("a[href]")) {
    const href = link.getAttribute("href");
    if (href.startsWith("#")) continue;
    link.href = resolve(href, baseUrl); link.target = "_blank"; link.rel = "noopener";
  }
  target.append(box);
}

/* ---------- video ---------- */
function youtubeId(url) {
  const m = url.match(/(?:v=|youtu\.be\/|embed\/)([\w-]{11})/);
  return m ? m[1] : null;
}
function mmss(seconds) { return `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`; }
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
    frame = h("iframe", { src: embedUrl(first, false), title: item.title, allowfullscreen: true,
      allow: "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" });
    body.append(h("div", { class: "video-wrap" }, frame));
  }
  if (id && clips.length) {
    const list = h("div", { class: "clips" }, h("strong", {}, "Assista só estes trechos (clique para ir ao trecho):"));
    clips.forEach((clip, index) => {
      const button = h("button", { class: "btn clip" + (index === 0 ? " on" : ""), onclick: () => {
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
    " ", h("a", { class: "btn", href: item.url, target: "_blank", rel: "noopener" }, icon("open_in_new"), "Abrir no YouTube")));
  if (item.summary) body.append(h("div", { class: "md", html: marked.parse(item.summary) }));
  if (item.review) body.append(reviewCard(item.review));
  if (item.transcript) {
    try {
      const transcript = await getJson(resolve(item.transcript, state.blockUrl));
      const seek = (second) => { if (id && frame) { frame.src = embedUrl({ start: second }, true); frame.scrollIntoView({ behavior: "smooth", block: "center" }); } };
      body.append(transcriptCard(transcript, clips, seek));
    } catch (error) { body.append(h("p", { class: "muted small" }, "Não consegui carregar a transcrição: " + error.message)); }
  }
}

/* Review: what reading the transcript showed, compared with the slide topics. */
function reviewCard(review) {
  const card = h("details", { class: "card" }, h("summary", {}, "Conferência com os slides (a partir da transcrição)"));
  card.append(h("p", { class: "muted small" }, "Eu li a transcrição do vídeo e comparei com os tópicos dos slides da professora. A transcrição é automática, então os tempos têm uma pequena margem de erro (poucos segundos a cerca de 15 s, conforme a fonte)."));
  if (review.covers?.length) card.append(h("strong", {}, "O que o vídeo cobre"), h("ul", {}, review.covers.map((x) => h("li", { html: marked.parseInline(x) }))));
  if (review.notCovered) card.append(h("strong", {}, "O que o vídeo não cobre"), h("p", { html: marked.parseInline(review.notCovered) }));
  if (review.profile?.length) card.append(h("strong", {}, "Perfil do vídeo"), h("ul", {}, review.profile.map((x) => h("li", { html: marked.parseInline(x) }))));
  if (review.verdict) card.append(h("strong", {}, "Conclusão"), h("p", { html: marked.parseInline(review.verdict) }));
  return card;
}

/* Transcript: shows the beginning; "Ver mais" opens everything. A timestamp jumps the video to that point. */
function transcriptCard(transcript, clips, seek) {
  const inClip = (second) => clips.some((c) => second >= c.start && second <= c.end);
  const lines = transcript.segments.map(([second, text]) =>
    h("p", { class: "line" + (inClip(second) ? " in" : "") },
      h("button", { class: "ts", title: "Ir para este ponto do vídeo", onclick: () => seek(second) }, mmss(second)), " ", text));
  const box = h("div", { class: "lines" }, lines);
  let chars = 0, visible = 0;                       // show the first lines up to ~700 characters
  for (const [, text] of transcript.segments) { chars += text.length; visible++; if (chars > 700) break; }
  lines.forEach((line, index) => { if (index >= visible) line.classList.add("extra"); });
  let open = false;
  const toggle = h("button", { class: "btn" }, "Ver mais");
  const card = h("div", { class: "card transcript" });
  toggle.onclick = () => { open = !open; card.classList.toggle("open", open); toggle.textContent = open ? "Ver menos" : "Ver mais"; };
  const language = transcript.lang === "pt" ? "português" : transcript.lang === "en" ? "inglês" : transcript.lang;
  const origin = /whisper/i.test(transcript.source || "") ? "Transcrição gerada por reconhecimento de fala (Whisper) a partir do áudio do vídeo"
    : `Legenda ${transcript.generated ? "automática" : "do autor"} do YouTube`;
  card.append(h("strong", {}, "Transcrição do vídeo"),
    h("p", { class: "muted small" }, `${origin}, em ${language}; pode ter erros de reconhecimento. Clique em um horário para ir àquele ponto do vídeo.${clips.length ? " Os trechos recomendados estão em destaque." : ""}`),
    box, toggle);
  return card;
}

/* ---------- questions ---------- */
async function renderQuestions(item, body) {
  const url = resolve(item.path, state.blockUrl);
  const set = await getJson(url);
  const answers = () => state.progress.answers[item.key] || {};
  const score = h("div", { class: "score" });
  const updateScore = async () => {
    const given = answers();
    const answered = set.questions.filter((q) => given[q.id]).length;
    const right = set.questions.filter((q) => given[q.id]?.correct).length;
    score.textContent = `Respondidas: ${answered}/${set.questions.length} · Acertos: ${right}`;
    if (answered === set.questions.length && !isDone(item)) await toggleDone(item, true);
  };
  if (set.instructions) body.append(h("div", { class: "md", html: marked.parse(set.instructions) }));
  body.append(score);
  let number = 0;
  for (const question of set.questions) {
    number++;
    const card = h("div", { class: "question" });
    body.append(card);
    let prompt = question.prompt || "";
    let base = url;
    if (question.promptFile) { base = resolve(question.promptFile, url); prompt = await getText(base); }
    const n = number;
    const draw = () => drawQuestion(card, question, n, prompt, base, answers()[question.id], {
      answer: async (chosen, correct) => { await mutate("PUT", `answers/${keyPath(item.key)}/${encodeURIComponent(question.id)}`, { chosen, correct }); draw(); updateScore(); },
      redo: async () => { await mutate("DELETE", `answers/${keyPath(item.key)}/${encodeURIComponent(question.id)}`); draw(); updateScore(); },
    });
    draw();
  }
  updateScore();
  if (set.closing) body.append(h("div", { class: "general md", html: marked.parse(set.closing) }));
}

function drawQuestion(card, question, number, prompt, base, saved, actions) {
  const multiple = question.type === "multiple";
  card.replaceChildren();
  card.className = "question" + (saved ? " answered" : "");
  card.append(h("div", { class: "qn" }, `Questão ${number}${question.label ? " · " + question.label : ""}${multiple ? " · marque todas as corretas" : ""}`));
  const promptBox = h("div");
  renderMarkdown(prompt, base, promptBox);
  card.append(promptBox);

  const chosen = new Set(saved ? saved.chosen : []);
  const inputs = [];
  for (const option of question.options) {
    const input = h("input", { type: multiple ? "checkbox" : "radio", name: "q-" + question.id, value: option.id, disabled: !!saved });
    input.checked = chosen.has(option.id);
    inputs.push(input);
    const marked_ = chosen.has(option.id);
    let cls = "option";
    if (saved) {
      if (option.correct && marked_) cls += " right";
      else if (!option.correct && marked_) cls += " wrong";
      else if (option.correct && !marked_) cls += " missed";
    }
    const content = h("div", { class: "body" }, h("div", { html: `<strong>${option.id.toUpperCase()})</strong> ` + marked.parseInline(option.text) }));
    if (saved && option.explanation) {
      const tag = option.correct ? (marked_ ? "Correta — você marcou." : "Correta — você não marcou.") : (marked_ ? "Errada — você marcou." : "Errada.");
      content.append(h("div", { class: "why" }, h("span", { class: "tag" }, tag + " "), h("span", { html: marked.parseInline(option.explanation) })));
    }
    card.append(h("label", { class: cls }, input, content));
  }

  if (!saved) {
    const button = h("button", { class: "btn primary", onclick: () => {
      const picked = inputs.filter((i) => i.checked).map((i) => i.value);
      if (!picked.length) { button.textContent = "Escolha uma alternativa primeiro"; return; }
      const rightIds = question.options.filter((o) => o.correct).map((o) => o.id).sort().join(",");
      actions.answer(picked, picked.slice().sort().join(",") === rightIds);
    } }, "Responder");
    card.append(button);
  } else {
    card.append(h("div", { class: "verdict " + (saved.correct ? "ok" : "no") }, saved.correct ? "Você acertou." : "Você errou. Leia a explicação de cada alternativa antes de seguir."));
    if (question.generalExplanation) {
      const general = h("div", { class: "general" });
      renderMarkdown(question.generalExplanation, base, general);
      card.append(general);
    }
    card.append(h("p", {}, h("button", { class: "btn", onclick: () => actions.redo() }, "Refazer esta questão")));
  }
}

/* ---------- choosing the data folder ---------- */
// The app never lists the disk. The user picks config.json in the operating system's own dialog, or pastes the path.
const DATA_FOLDER_HINT = "Neste projeto é a pasta conteudo, dentro de estudo, na pasta do Google Drive da disciplina (…/Mestrado/2026.2 - Aprend. máquina/estudo/conteudo). Dentro dela está o arquivo config.json.";
async function showSetup(message) {
  document.body.classList.remove("menu-open");
  $("#sidebar").replaceChildren();
  const main = $("#main");
  const info = state.setup || (state.setup = await getJson("/api/setup"));
  const input = h("input", { class: "path-input", type: "text", spellcheck: "false", placeholder: "…ou cole aqui o caminho da pasta de dados" });
  const status = h("p", { class: "muted" });
  const useButton = h("button", { class: "btn primary" }, "Usar esta pasta");
  const pickButton = h("button", { class: "btn" }, "Escolher o arquivo config.json…");

  pickButton.onclick = async () => {
    status.textContent = "Aguardando a janela de seleção do sistema (ela pode abrir atrás deste navegador)…"; status.className = "muted";
    pickButton.disabled = true;
    try {
      const response = await fetch("/api/setup/pick", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      const result = await response.json();
      if (!response.ok) { status.textContent = result.message || result.error; status.className = "bad-text"; }
      else if (!result.available) { status.textContent = "Este computador não tem o seletor de arquivos do Python (no Linux: instale o pacote python3-tk). Cole o caminho no campo ao lado."; status.className = "bad-text"; }
      else if (result.cancelled) { status.textContent = "Nenhum arquivo escolhido."; status.className = "muted"; }
      else { input.value = result.folder; status.textContent = result.isDataDir ? "Pasta encontrada. Confira o caminho e clique em “Usar esta pasta”." : "A pasta escolhida não tem um config.json. Escolha o arquivo config.json da pasta de dados."; status.className = result.isDataDir ? "ok-text" : "bad-text"; }
    } catch (error) { status.textContent = "Não consegui abrir o seletor: " + error.message; status.className = "bad-text"; }
    pickButton.disabled = false;
  };
  useButton.onclick = async () => {
    const path = input.value.trim();
    if (!path) { status.textContent = "Escolha o arquivo config.json ou cole o caminho da pasta."; status.className = "bad-text"; return; }
    const response = await fetch("/api/setup", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path }) });
    if (!response.ok) { const err = await response.json(); status.textContent = err.message || err.error; status.className = "bad-text"; return; }
    location.reload();
  };
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") useButton.click(); });
  main.replaceChildren(...[
    h("h1", { class: "page-title" }, "Onde estão os arquivos do curso?"),
    message ? h("p", {}, message) : null,
    h("p", {}, "O app precisa saber qual é a pasta de dados: a que contém o arquivo ", h("code", {}, "config.json"),
      " (aulas, figuras, transcrições e o seu progresso). A escolha fica salva neste computador; em outro computador, escolha de novo."),
    h("div", { class: "goals" }, h("strong", {}, "Onde encontrar"), h("p", {}, DATA_FOLDER_HINT)),
    info.savedDir ? h("p", { class: "muted small" }, "Pasta salva anteriormente (não encontrada ou sem config.json): " + info.savedDir) : null,
    h("p", {}, pickButton),
    h("div", { class: "path-row" }, input, useButton),
    status,
    h("p", { class: "muted small" }, "O app não lista o disco: ele só conhece o caminho que você escolher ou colar. Depois de escolhida, ele lê apenas arquivos dentro da pasta de dados."),
  ].filter(Boolean));
}

/* ---------- start ---------- */
async function start() {
  await loadIcons();
  $("#menu-btn").replaceChildren(icon("menu"));
  $("#menu-btn").addEventListener("click", () => document.body.classList.toggle("menu-open"));
  state.setup = await getJson("/api/setup");
  if (!state.setup.configured) { await showSetup(); return; }
  state.config = await getJson("/api/config");
  if (!(await reloadProgress())) throw new Error("A API de progresso não respondeu.");
  const select = $("#block-select");
  for (const block of state.config.blocks) select.append(h("option", { value: block.id }, block.title));
  select.addEventListener("change", () => { history.replaceState(null, "", "#"); openBlock(select.value); });
  const wanted = location.hash.slice(1).split("/")[0];
  await openBlock(state.config.blocks.some((b) => b.id === wanted) ? wanted : state.config.blocks[0].id);
}
start().catch((error) => {
  $("#main").replaceChildren(h("div", { class: "verdict no" }, "Não consegui iniciar: " + error.message),
    h("p", {}, "Inicie a API com: study serve  e abra http://localhost:8765/"));
});
