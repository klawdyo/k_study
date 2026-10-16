"""Consultas SQL do painel do admin (somente leitura). Cada função recebe uma conexão sqlite3 e devolve dados JSON.

Esquema v2 (docs/arquitetura.md, seção 4): todo aluno traz `name` e `email`; toda trilha traz `active`.
As funções só leem: recebem uma conexão sqlite3 com row_factory = sqlite3.Row e não conhecem HTTP.

Convenções
  * Tempo em segundos inteiros; datas em ISO 8601 UTC; taxas em fração 0..1 (None quando não há base de cálculo).
  * "Item obrigatório" = items.optional = 0. "Item feito" = progress.done = 1 em um item que existe no índice.
  * "Só abriu e saiu" = visita com seconds < QUICK_SECONDS (10).
  * Aluno "iniciou" uma trilha se tem visita, progresso ou resposta nela; a conclusão média considera só quem iniciou.
  * Aluno "ativo em 7 dias" = last_seen_at ou alguma visita nos últimos 7 dias.
  * A conclusão de um aluno em uma trilha = itens obrigatórios feitos / itens obrigatórios (0..1).

Formato das respostas (as chaves são em inglês; a interface depende delas)

overview():
  {"generated_at": iso,
   "totals": {"students", "active_7d", "seconds", "visits", "quick_visits", "trails", "answers", "accuracy"},
   "daily": [{"date": "YYYY-MM-DD", "seconds", "active_students", "visits"}]       # 30 dias, o último é hoje
   "trails": [{"slug", "title", "students", "avg_completion"}]                       # conclusão maior primeiro
   "hardest_questions": [{"trail", "trail_title", "block_id", "item_id", "item_title", "question_id",
                          "answers", "wrong", "error_rate"}]                         # até 8
   "abandoned_items":   [{"trail", "trail_title", "block_id", "item_id", "title", "type", "visits", "quick_visits",
                          "abandon_rate"}]                                           # até 8, mínimo 3 visitas
   "recent": [{"at", "kind": "visit"|"answer"|"done", "student_id", "name", "email", "trail", "trail_title", "item_id",
               "title", "detail"}]}                                                  # até 15

students():
  {"students": [{"id", "name", "email", "created_at", "last_activity", "seconds", "visits", "quick_visits",
                 "items_done", "required_done", "answers", "correct", "accuracy"}]}

student(id):  (None se não existe)
  {"student": {"id", "name", "email", "created_at", "last_activity", "seconds", "visits", "quick_visits", "items_done",
               "answers", "correct", "accuracy"},
   "trails": [{"slug", "title", "required_items", "required_done", "items_done", "completion", "seconds",
               "visits", "quick_visits", "answers", "correct", "accuracy",
               "items": [{"block_id", "block_title", "item_id", "title", "type", "section", "optional", "done",
                          "seconds", "visits", "quick_visits",
                          "questions": [{"question_id", "correct", "chosen", "at"}]}]}]}

trails():
  {"trails": [{"slug", "title", "description", "cover" (URL ou None), "active" (bool), "blocks", "items", "required_items", "students", "active_7d",
               "avg_completion", "seconds", "avg_seconds", "visits", "accuracy"}]}

trail(slug):  (None se não existe)
  {"trail": {... os mesmos campos de trails()},
   "blocks": [{"block_id", "title", "students_opened", "seconds", "avg_completion", "abandon_rate", "accuracy",
               "sections": [{"title", "items": [{"item_id", "title", "type", "optional", "students_opened",
                          "visits", "quick_visits", "seconds", "avg_seconds", "abandon_rate", "done", "completion",
                          "answers", "correct", "accuracy"}]}]}],
   "hardest_questions": [{"block_id", "item_id", "item_title", "question_id", "answers", "wrong", "error_rate"}]}
"""
import json
from datetime import datetime, timedelta, timezone

QUICK_SECONDS = 10
ACTIVE_DAYS = 7
DAILY_DAYS = 30
MIN_VISITS_ABANDON = 3
MIN_ANSWERS_HARD = 2


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def _rate(num, den):
    return round(num / den, 4) if den else None


def _max_str(*values):
    values = [v for v in values if v]
    return max(values) if values else None


def _rows(conn, sql, params=()):
    return conn.execute(sql, params).fetchall()


def _trail_titles(conn) -> dict:
    return {r["slug"]: r["title"] or r["slug"] for r in _rows(conn, "SELECT slug, title FROM trails")}


def _required_counts(conn) -> dict:
    """slug -> (itens, obrigatórios)."""
    return {r["trail"]: (r["n"], r["req"] or 0) for r in _rows(
        conn, "SELECT trail, COUNT(*) n, SUM(CASE WHEN COALESCE(optional,0)=0 THEN 1 ELSE 0 END) req "
              "FROM items GROUP BY trail")}


def _empty_stats() -> dict:
    return {"seconds": 0, "visits": 0, "quick": 0, "done": 0, "required_done": 0, "answers": 0, "correct": 0}


def _student_trail_stats(conn) -> dict:
    """(student_id, trail) -> {seconds, visits, quick, done, required_done, answers, correct}."""
    out: dict = {}

    def slot(sid, trail):
        return out.setdefault((sid, trail), _empty_stats())

    for r in _rows(conn, "SELECT student_id sid, trail, SUM(seconds) s, COUNT(*) n, "
                         "SUM(CASE WHEN seconds < ? THEN 1 ELSE 0 END) q FROM visits GROUP BY student_id, trail",
                   (QUICK_SECONDS,)):
        d = slot(r["sid"], r["trail"])
        d["seconds"], d["visits"], d["quick"] = r["s"] or 0, r["n"], r["q"] or 0
    for r in _rows(conn, "SELECT p.student_id sid, p.trail trail, COUNT(*) n, "
                         "SUM(CASE WHEN COALESCE(i.optional,0)=0 THEN 1 ELSE 0 END) req "
                         "FROM progress p JOIN items i ON i.trail=p.trail AND i.block_id=p.block_id AND i.item_id=p.item_id "
                         "WHERE p.done=1 GROUP BY p.student_id, p.trail"):
        d = slot(r["sid"], r["trail"])
        d["done"], d["required_done"] = r["n"], r["req"] or 0
    for r in _rows(conn, "SELECT student_id sid, trail, COUNT(*) n, SUM(CASE WHEN correct=1 THEN 1 ELSE 0 END) c "
                         "FROM answers GROUP BY student_id, trail"):
        d = slot(r["sid"], r["trail"])
        d["answers"], d["correct"] = r["n"], r["c"] or 0
    return out


def _last_activity(conn) -> dict:
    """student_id -> data mais recente de qualquer atividade."""
    last: dict = {}

    def feed(sql):
        for r in _rows(conn, sql):
            last[r["sid"]] = _max_str(last.get(r["sid"]), r["at"])

    feed("SELECT id sid, last_seen_at at FROM students")
    feed("SELECT student_id sid, MAX(COALESCE(last_beat_at, started_at)) at FROM visits GROUP BY student_id")
    feed("SELECT student_id sid, MAX(started_at) at FROM visits GROUP BY student_id")
    feed("SELECT student_id sid, MAX(at) at FROM progress GROUP BY student_id")
    feed("SELECT student_id sid, MAX(at) at FROM answers GROUP BY student_id")
    return last


def _started(s: dict) -> bool:
    return bool(s["visits"] or s["done"] or s["answers"])


def _completion(stats: dict, required: int):
    return min(1.0, round(stats["required_done"] / required, 4)) if required else None


def _avg(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 4) if values else None


def _trail_summaries(conn, now: datetime) -> list:
    titles = _trail_titles(conn)
    counts = _required_counts(conn)
    meta = {r["slug"]: r for r in _rows(conn, "SELECT slug, description, cover, active FROM trails")}
    blocks_n = {r["trail"]: r["n"] for r in _rows(conn, "SELECT trail, COUNT(*) n FROM blocks GROUP BY trail")}
    stats = _student_trail_stats(conn)
    cutoff = _iso(now - timedelta(days=ACTIVE_DAYS))
    active = {r["trail"]: r["n"] for r in _rows(
        conn, "SELECT trail, COUNT(DISTINCT student_id) n FROM visits WHERE started_at >= ? GROUP BY trail", (cutoff,))}
    out = []
    for slug in titles:
        items, required = counts.get(slug, (0, 0))
        mine = [s for (sid, t), s in stats.items() if t == slug and _started(s)]
        seconds = sum(s["seconds"] for s in mine)
        answers = sum(s["answers"] for s in mine)
        out.append({
            "slug": slug, "title": titles[slug], "description": (meta[slug]["description"] or "") if slug in meta else "",
            "cover": f"/api/trails/{slug}/cover" if slug in meta and meta[slug]["cover"] else None,
            "active": bool(meta[slug]["active"]) if slug in meta else True,
            "blocks": blocks_n.get(slug, 0), "items": items, "required_items": required,
            "students": len(mine), "active_7d": active.get(slug, 0),
            "avg_completion": _avg([_completion(s, required) for s in mine]),
            "seconds": seconds, "avg_seconds": round(seconds / len(mine)) if mine else 0,
            "visits": sum(s["visits"] for s in mine),
            "accuracy": _rate(sum(s["correct"] for s in mine), answers),
        })
    return out


def _hardest(conn, trail=None, limit=8) -> list:
    where, params = ("WHERE a.trail = ?", [trail]) if trail else ("", [])
    sql = ("SELECT a.trail, a.block_id, a.item_id, a.question_id, COUNT(*) n, "
           "SUM(CASE WHEN a.correct=1 THEN 0 ELSE 1 END) wrong, MAX(i.title) item_title "
           "FROM answers a LEFT JOIN items i ON i.trail=a.trail AND i.block_id=a.block_id AND i.item_id=a.item_id "
           f"{where} GROUP BY a.trail, a.block_id, a.item_id, a.question_id HAVING COUNT(*) >= ? "
           "ORDER BY CAST(SUM(CASE WHEN a.correct=1 THEN 0 ELSE 1 END) AS REAL)/COUNT(*) DESC, wrong DESC LIMIT ?")
    titles = _trail_titles(conn)
    out = []
    for r in _rows(conn, sql, params + [MIN_ANSWERS_HARD, limit]):
        if not r["wrong"]:
            continue
        d = {"block_id": r["block_id"], "item_id": r["item_id"], "item_title": r["item_title"] or r["item_id"],
             "question_id": r["question_id"], "answers": r["n"], "wrong": r["wrong"],
             "error_rate": _rate(r["wrong"], r["n"])}
        if not trail:
            d["trail"], d["trail_title"] = r["trail"], titles.get(r["trail"], r["trail"])
        out.append(d)
    return out


def overview(conn, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    cutoff = _iso(now - timedelta(days=ACTIVE_DAYS))
    titles = _trail_titles(conn)
    n_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM students s WHERE s.last_seen_at >= ? OR EXISTS "
                          "(SELECT 1 FROM visits v WHERE v.student_id = s.id AND v.started_at >= ?)",
                          (cutoff, cutoff)).fetchone()[0]
    v = conn.execute("SELECT COALESCE(SUM(seconds),0), COUNT(*), COALESCE(SUM(CASE WHEN seconds < ? THEN 1 ELSE 0 END),0) "
                     "FROM visits", (QUICK_SECONDS,)).fetchone()
    a = conn.execute("SELECT COUNT(*), COALESCE(SUM(CASE WHEN correct=1 THEN 1 ELSE 0 END),0) FROM answers").fetchone()
    first = (now - timedelta(days=DAILY_DAYS - 1)).strftime("%Y-%m-%d")
    by_day = {r["d"]: r for r in _rows(
        conn, "SELECT substr(started_at,1,10) d, COALESCE(SUM(seconds),0) s, COUNT(*) n, COUNT(DISTINCT student_id) st "
              "FROM visits WHERE substr(started_at,1,10) >= ? GROUP BY d", (first,))}
    daily = []
    for k in range(DAILY_DAYS):
        day = (now - timedelta(days=DAILY_DAYS - 1 - k)).strftime("%Y-%m-%d")
        r = by_day.get(day)
        daily.append({"date": day, "seconds": r["s"] if r else 0, "visits": r["n"] if r else 0,
                      "active_students": r["st"] if r else 0})
    trails_list = sorted(({"slug": t["slug"], "title": t["title"], "students": t["students"],
                           "avg_completion": t["avg_completion"]} for t in _trail_summaries(conn, now)),
                         key=lambda t: (t["avg_completion"] is None, -(t["avg_completion"] or 0), t["title"]))
    abandoned = []
    for r in _rows(conn, "SELECT v.trail, v.block_id, v.item_id, COUNT(*) n, "
                         "SUM(CASE WHEN v.seconds < ? THEN 1 ELSE 0 END) q, MAX(i.title) title, MAX(i.type) type "
                         "FROM visits v LEFT JOIN items i ON i.trail=v.trail AND i.block_id=v.block_id AND i.item_id=v.item_id "
                         "GROUP BY v.trail, v.block_id, v.item_id HAVING COUNT(*) >= ? "
                         "ORDER BY CAST(SUM(CASE WHEN v.seconds < ? THEN 1 ELSE 0 END) AS REAL)/COUNT(*) DESC, q DESC LIMIT 8",
                   (QUICK_SECONDS, MIN_VISITS_ABANDON, QUICK_SECONDS)):
        if not r["q"]:
            continue
        abandoned.append({"trail": r["trail"], "trail_title": titles.get(r["trail"], r["trail"]),
                          "block_id": r["block_id"], "item_id": r["item_id"], "title": r["title"] or r["item_id"],
                          "type": r["type"], "visits": r["n"], "quick_visits": r["q"],
                          "abandon_rate": _rate(r["q"], r["n"])})
    return {
        "generated_at": _iso(now),
        "totals": {"students": n_students, "active_7d": active, "seconds": v[0], "visits": v[1], "quick_visits": v[2],
                   "trails": len(titles), "answers": a[0], "accuracy": _rate(a[1], a[0])},
        "daily": daily, "trails": trails_list, "hardest_questions": _hardest(conn),
        "abandoned_items": abandoned, "recent": _recent(conn, titles),
    }


def _recent(conn, titles, limit=15) -> list:
    base = ("{sel} FROM {tbl} x JOIN students s ON s.id = x.student_id "
            "LEFT JOIN items i ON i.trail=x.trail AND i.block_id=x.block_id AND i.item_id=x.item_id "
            "{where} ORDER BY at DESC LIMIT ?")
    parts = [
        ("visit", "SELECT x.started_at at, x.student_id sid, s.name, s.email, x.trail, x.item_id, i.title, x.seconds det",
         "visits", ""),
        ("answer", "SELECT x.at at, x.student_id sid, s.name, s.email, x.trail, x.item_id, i.title, x.correct det",
         "answers", ""),
        ("done", "SELECT x.at at, x.student_id sid, s.name, s.email, x.trail, x.item_id, i.title, 1 det", "progress",
         "WHERE x.done = 1"),
    ]
    events = []
    for kind, sel, tbl, where in parts:
        for r in _rows(conn, base.format(sel=sel, tbl=tbl, where=where), (limit,)):
            if not r["at"]:
                continue
            det = r["det"]
            if kind == "visit":
                detail = f"{det or 0} s"
            elif kind == "answer":
                detail = "acertou" if det else "errou"
            else:
                detail = "concluiu"
            events.append({"at": r["at"], "kind": kind, "student_id": r["sid"], "name": r["name"] or "", "email": r["email"], "trail": r["trail"],
                           "trail_title": titles.get(r["trail"], r["trail"]), "item_id": r["item_id"],
                           "title": r["title"] or r["item_id"], "detail": detail})
    events.sort(key=lambda e: e["at"], reverse=True)
    return events[:limit]


def students(conn) -> dict:
    stats = _student_trail_stats(conn)
    last = _last_activity(conn)
    totals: dict = {}
    for (sid, _t), s in stats.items():
        d = totals.setdefault(sid, _empty_stats())
        for k in d:
            d[k] += s[k]
    out = []
    for r in _rows(conn, "SELECT id, name, email, created_at FROM students ORDER BY email"):
        t = totals.get(r["id"]) or _empty_stats()
        out.append({"id": r["id"], "name": r["name"] or "", "email": r["email"], "created_at": r["created_at"], "last_activity": last.get(r["id"]),
                    "seconds": t["seconds"], "visits": t["visits"], "quick_visits": t["quick"], "items_done": t["done"],
                    "required_done": t["required_done"], "answers": t["answers"], "correct": t["correct"],
                    "accuracy": _rate(t["correct"], t["answers"])})
    return {"students": out}


def student(conn, student_id: int) -> dict | None:
    row = conn.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        return None
    titles = _trail_titles(conn)
    counts = _required_counts(conn)
    stats = {t: s for (sid, t), s in _student_trail_stats(conn).items() if sid == student_id}
    visit = {(r["trail"], r["block_id"], r["item_id"]): r for r in _rows(
        conn, "SELECT trail, block_id, item_id, SUM(seconds) s, COUNT(*) n, "
              "SUM(CASE WHEN seconds < ? THEN 1 ELSE 0 END) q FROM visits WHERE student_id = ? "
              "GROUP BY trail, block_id, item_id", (QUICK_SECONDS, student_id))}
    done = {(r["trail"], r["block_id"], r["item_id"]) for r in _rows(
        conn, "SELECT trail, block_id, item_id FROM progress WHERE student_id = ? AND done = 1", (student_id,))}
    questions: dict = {}
    for r in _rows(conn, "SELECT trail, block_id, item_id, question_id, chosen, correct, at FROM answers "
                         "WHERE student_id = ? ORDER BY question_id", (student_id,)):
        try:
            chosen = json.loads(r["chosen"]) if r["chosen"] else []
        except ValueError:
            chosen = [r["chosen"]]
        questions.setdefault((r["trail"], r["block_id"], r["item_id"]), []).append(
            {"question_id": r["question_id"], "correct": bool(r["correct"]), "chosen": chosen, "at": r["at"]})
    indexed = _rows(conn, "SELECT i.trail, i.block_id, i.item_id, i.section, i.type, i.title, COALESCE(i.optional,0) optional, "
                          "b.title block_title FROM items i LEFT JOIN blocks b ON b.trail=i.trail AND b.block_id=i.block_id "
                          "ORDER BY i.trail, COALESCE(b.position, 9999), i.block_id, i.position")
    by_trail: dict = {}
    for r in indexed:
        by_trail.setdefault(r["trail"], []).append(r)
    trail_list = []
    for slug, rows in by_trail.items():
        s = stats.get(slug)
        if not s or not _started(s):
            continue
        items = []
        for r in rows:
            key = (slug, r["block_id"], r["item_id"])
            vis = visit.get(key)
            qs = questions.get(key, [])
            if not (vis or key in done or qs):
                continue
            items.append({"block_id": r["block_id"], "block_title": r["block_title"] or r["block_id"],
                          "item_id": r["item_id"], "title": r["title"] or r["item_id"], "type": r["type"],
                          "section": r["section"], "optional": bool(r["optional"]), "done": key in done,
                          "seconds": (vis["s"] or 0) if vis else 0, "visits": vis["n"] if vis else 0,
                          "quick_visits": (vis["q"] or 0) if vis else 0, "questions": qs})
        req = counts.get(slug, (0, 0))[1]
        trail_list.append({"slug": slug, "title": titles.get(slug, slug), "required_items": req,
                           "required_done": s["required_done"], "items_done": s["done"],
                           "completion": _completion(s, req), "seconds": s["seconds"], "visits": s["visits"],
                           "quick_visits": s["quick"], "answers": s["answers"], "correct": s["correct"],
                           "accuracy": _rate(s["correct"], s["answers"]), "items": items})
    me = next(x for x in students(conn)["students"] if x["id"] == student_id)
    return {"student": {k: me[k] for k in ("id", "name", "email", "created_at", "last_activity", "seconds", "visits",
                                           "quick_visits", "items_done", "answers", "correct", "accuracy")},
            "trails": trail_list}


def trails(conn, now: datetime | None = None) -> dict:
    return {"trails": _trail_summaries(conn, now or datetime.now(timezone.utc))}


def trail(conn, slug: str, now: datetime | None = None) -> dict | None:
    summary = next((t for t in _trail_summaries(conn, now or datetime.now(timezone.utc)) if t["slug"] == slug), None)
    if summary is None:
        return None
    n_students = summary["students"]
    vis = {(r["block_id"], r["item_id"]): r for r in _rows(
        conn, "SELECT block_id, item_id, SUM(seconds) s, COUNT(*) n, COUNT(DISTINCT student_id) st, "
              "SUM(CASE WHEN seconds < ? THEN 1 ELSE 0 END) q FROM visits WHERE trail = ? GROUP BY block_id, item_id",
        (QUICK_SECONDS, slug))}
    done = {(r["block_id"], r["item_id"]): r["n"] for r in _rows(
        conn, "SELECT block_id, item_id, COUNT(*) n FROM progress WHERE trail = ? AND done = 1 GROUP BY block_id, item_id",
        (slug,))}
    ans = {(r["block_id"], r["item_id"]): r for r in _rows(
        conn, "SELECT block_id, item_id, COUNT(*) n, SUM(CASE WHEN correct=1 THEN 1 ELSE 0 END) c FROM answers "
              "WHERE trail = ? GROUP BY block_id, item_id", (slug,))}
    block_rows = _rows(conn, "SELECT block_id, title FROM blocks WHERE trail = ? ORDER BY position", (slug,))
    item_rows = _rows(conn, "SELECT block_id, item_id, section, type, title, COALESCE(optional,0) optional "
                            "FROM items WHERE trail = ? ORDER BY position", (slug,))
    by_block: dict = {}
    for r in item_rows:
        by_block.setdefault(r["block_id"], []).append(r)
    order = [(b["block_id"], b["title"]) for b in block_rows]
    known = {b for b, _ in order}
    order += [(b, b) for b in by_block if b not in known]
    done_by_block: dict = {}   # bloco -> lista de (obrigatórios feitos) por aluno
    for r in _rows(conn, "SELECT p.block_id b, COUNT(*) n FROM progress p JOIN items i ON "
                         "i.trail=p.trail AND i.block_id=p.block_id AND i.item_id=p.item_id "
                         "WHERE p.trail = ? AND p.done = 1 AND COALESCE(i.optional,0)=0 "
                         "GROUP BY p.student_id, p.block_id", (slug,)):
        done_by_block.setdefault(r["b"], []).append(r["n"])
    blocks = []
    for block_id, title in order:
        rows = by_block.get(block_id, [])
        sections: dict = {}
        b_sec = b_vis = b_quick = b_ans = b_cor = openers = 0
        for r in rows:
            key = (block_id, r["item_id"])
            v, a = vis.get(key), ans.get(key)
            n_vis = v["n"] if v else 0
            quick = (v["q"] or 0) if v else 0
            sec = (v["s"] or 0) if v else 0
            st = v["st"] if v else 0
            d = done.get(key, 0)
            item = {"item_id": r["item_id"], "title": r["title"] or r["item_id"], "type": r["type"],
                    "optional": bool(r["optional"]), "students_opened": st, "visits": n_vis, "quick_visits": quick,
                    "seconds": sec, "avg_seconds": round(sec / st) if st else 0, "abandon_rate": _rate(quick, n_vis),
                    "done": d, "completion": _rate(d, n_students),
                    "answers": a["n"] if a else 0, "correct": (a["c"] or 0) if a else 0,
                    "accuracy": _rate(a["c"] or 0, a["n"]) if a else None}
            sections.setdefault(r["section"] or "", []).append(item)
            b_sec += sec
            b_vis += n_vis
            b_quick += quick
            openers = max(openers, st)
            if a:
                b_ans += a["n"]
                b_cor += a["c"] or 0
        req_block = sum(1 for r in rows if not r["optional"])
        per_student = [min(1.0, n / req_block) for n in done_by_block.get(block_id, [])] if req_block else []
        if req_block:
            per_student += [0.0] * max(0, n_students - len(per_student))   # quem iniciou a trilha e nada fez aqui conta 0
        blocks.append({"block_id": block_id, "title": title or block_id, "students_opened": openers, "seconds": b_sec,
                       "avg_completion": _avg(per_student), "abandon_rate": _rate(b_quick, b_vis),
                       "accuracy": _rate(b_cor, b_ans),
                       "sections": [{"title": t, "items": its} for t, its in sections.items()]})
    return {"trail": summary, "blocks": blocks, "hardest_questions": _hardest(conn, slug, 10)}
