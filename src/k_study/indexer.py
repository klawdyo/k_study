"""Lê content/<slug>/trail.json (+ cada block.json) e atualiza o índice no banco.

O índice é só um espelho barato do conteúdo (listar trilhas, contar itens, estimar minutos). O corpo das aulas
continua nos arquivos. Progresso, respostas, anotações e visitas NUNCA são apagados aqui.
Reindexa uma trilha quando muda a assinatura (soma dos mtimes do trail.json e dos block.json) ou com force=True.
Mudanças só no texto de uma leitura (.md) não alteram a assinatura: use `kstudy sync --force` para recalcular minutos.
"""
import json
import os
import re
import threading
from pathlib import Path

from .db import Database, now

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WORDS_PER_MINUTE = 180
ITEM_EXTENSIONS = {".json", ".md", ".pdf"}                 # arquivos de aula servíveis
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
COVER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_lock = threading.Lock()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def trail_dirs(content_dir: Path) -> list[Path]:
    """Pastas de trilha válidas por nome (slug) que têm trail.json."""
    if not content_dir.is_dir():
        return []
    return sorted(p for p in content_dir.iterdir()
                  if p.is_dir() and SLUG.match(p.name) and (p / "trail.json").is_file())


def signature(folder: Path, manifest: dict) -> float:
    """Soma dos mtimes do trail.json e dos block.json citados (muda se qualquer um mudar)."""
    total = (folder / "trail.json").stat().st_mtime
    for entry in manifest.get("blocks") or []:
        try:
            total += (folder / str(entry.get("file", ""))).stat().st_mtime
        except (OSError, AttributeError):
            total += 1.0          # arquivo ausente conta como mudança quando aparecer
    return total


def estimate_minutes(item: dict, block_dir: Path) -> float | None:
    """Vídeo: soma dos trechos (clips), ou start/end, ou 'duration'. Leitura: palavras / 180. Outros: None."""
    kind = item.get("type")
    if kind == "video":
        clips = item.get("clips") or []
        seconds = sum(max(0, c.get("end", 0) - c.get("start", 0)) for c in clips if isinstance(c, dict))
        if not seconds and "start" in item and "end" in item:
            seconds = max(0, item["end"] - item["start"])
        if seconds:
            return round(seconds / 60, 1)
        found = re.search(r"(\d+)", str(item.get("duration", "")))
        return float(found.group(1)) if found else None
    if kind == "markdown" and item.get("path"):
        try:
            text = (block_dir / item["path"]).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        return float(max(1, round(len(text.split()) / WORDS_PER_MINUTE)))
    return None


def safe_relative(folder: Path, base: Path, relative, extensions: set) -> str | None:
    """Caminho (relativo à pasta da trilha, com `/`) de `relative` resolvido a partir de `base`.
    None se sair da pasta da trilha, não for arquivo ou tiver extensão fora da lista permitida."""
    if not isinstance(relative, str) or not relative or "\x00" in relative or "\\" in relative:
        return None
    try:
        root = folder.resolve()
        target = (base / relative).resolve()
    except (OSError, ValueError):
        return None
    if root not in target.parents or not target.is_file() or target.suffix.lower() not in extensions:
        return None
    return target.relative_to(root).as_posix()


def _asset(conn, slug: str, folder: Path, relative: str, kind: str) -> None:
    conn.execute("INSERT OR REPLACE INTO assets(trail, path, kind, size) VALUES(?,?,?,?)",
                 (slug, relative, kind, (folder / relative).stat().st_size))


def _index_trail(conn, folder: Path, manifest: dict, mtime: float) -> None:
    slug = folder.name
    cover = safe_relative(folder, folder, manifest.get("cover"), COVER_EXTENSIONS)
    conn.execute("INSERT INTO trails(slug, title, description, language, level, tags, cover, manifest_mtime, synced_at) "
                 "VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(slug) DO UPDATE SET title=excluded.title, "
                 "description=excluded.description, language=excluded.language, level=excluded.level, "
                 "tags=excluded.tags, cover=excluded.cover, manifest_mtime=excluded.manifest_mtime, "
                 "synced_at=excluded.synced_at",         # `active` não é tocado: a decisão do admin sobrevive
                 (slug, manifest.get("title") or slug, manifest.get("description") or "", manifest.get("language"),
                  manifest.get("level"), json.dumps(manifest.get("tags") or [], ensure_ascii=False), cover, mtime, now()))
    conn.execute("DELETE FROM blocks WHERE trail=?", (slug,))
    conn.execute("DELETE FROM items WHERE trail=?", (slug,))
    conn.execute("DELETE FROM assets WHERE trail=?", (slug,))
    if cover:
        _asset(conn, slug, folder, cover, "cover")
    figures = folder / "figures"
    if figures.is_dir():
        for image in sorted(figures.iterdir()):
            relative = safe_relative(folder, folder, f"figures/{image.name}", IMAGE_EXTENSIONS)
            if relative and re.match(r"^[A-Za-z0-9._-]+$", image.name):
                _asset(conn, slug, folder, relative, "figure")
    for position, entry in enumerate(manifest.get("blocks") or []):
        if not isinstance(entry, dict) or not entry.get("id"):
            continue
        block_path = folder / str(entry.get("file", ""))
        try:
            block = read_json(block_path)
        except (OSError, ValueError):
            block = {}
        conn.execute("INSERT OR REPLACE INTO blocks(trail, block_id, title, position, file) VALUES(?,?,?,?,?)",
                     (slug, entry["id"], entry.get("title") or block.get("title") or entry["id"], position,
                      entry.get("file")))
        block_file = safe_relative(folder, folder, entry.get("file"), {".json"})
        if block_file:
            _asset(conn, slug, folder, block_file, "block")
        order = 0
        for section in block.get("sections") or []:
            for item in section.get("items") or []:
                if not isinstance(item, dict) or not item.get("id") or not item.get("type"):
                    continue
                item_file = safe_relative(folder, block_path.parent, item.get("path"), ITEM_EXTENSIONS)
                transcript = safe_relative(folder, block_path.parent, item.get("transcript"), {".json"})
                if item_file:
                    _asset(conn, slug, folder, item_file, "item")
                if transcript:
                    _asset(conn, slug, folder, transcript, "transcript")
                conn.execute("INSERT OR REPLACE INTO items(trail, block_id, item_id, section, position, type, title, "
                             "path, transcript, optional, minutes) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                             (slug, entry["id"], item["id"], section.get("id"), order, item["type"],
                              item.get("title") or item["id"], item_file, transcript, 1 if item.get("optional") else 0,
                              estimate_minutes(item, block_path.parent)))
                order += 1


def sync(content_dir, db: Database, force: bool = False) -> dict:
    """Sincroniza o índice com content/. Devolve {'indexed': [...], 'removed': [...], 'skipped': {slug: motivo}}."""
    content_dir = Path(content_dir)
    result = {"indexed": [], "removed": [], "skipped": {}}
    with _lock:
        present = set()
        for folder in trail_dirs(content_dir):
            slug = folder.name
            present.add(slug)
            try:
                manifest = read_json(folder / "trail.json")
                if not isinstance(manifest, dict):
                    raise ValueError("o trail.json deve ser um objeto")
                if manifest.get("id") != slug:
                    raise ValueError(f"o id do trail.json ({manifest.get('id')!r}) difere do nome da pasta")
                mtime = signature(folder, manifest)
            except (OSError, ValueError) as exc:
                result["skipped"][slug] = str(exc)
                continue
            row = db.one("SELECT manifest_mtime FROM trails WHERE slug=?", (slug,))
            if row is not None and not force and abs((row["manifest_mtime"] or 0) - mtime) < 1e-6:
                continue
            with db.tx() as conn:
                _index_trail(conn, folder, manifest, mtime)
            result["indexed"].append(slug)
        for row in db.query("SELECT slug FROM trails"):
            # trilha com pasta ainda presente mas trail.json quebrado (skipped) permanece no índice
            if row["slug"] not in present:
                with db.tx() as conn:
                    conn.execute("DELETE FROM items WHERE trail=?", (row["slug"],))
                    conn.execute("DELETE FROM blocks WHERE trail=?", (row["slug"],))
                    conn.execute("DELETE FROM assets WHERE trail=?", (row["slug"],))
                    conn.execute("DELETE FROM trails WHERE slug=?", (row["slug"],))
                result["removed"].append(row["slug"])
    return result
