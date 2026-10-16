"""Pacotes zip do k_study: importar trilha, empacotar trilha e zip das specs (docs/arquitetura.md, 3.1 e 11.1).

Apenas biblioteca padrão. A importação verifica TUDO antes de extrair, extrai numa pasta temporária dentro de
`content_dir`, roda o validador e só então move a pasta para o lugar (troca atômica com `replace`).
Nada do conteúdo é executado.
"""
import io
import re
import zlib
import shutil
import tempfile
import threading
import zipfile
from pathlib import Path, PurePosixPath

from . import validate as validator

ALLOWED_EXTENSIONS = {".json", ".md", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".txt"}
TEXT_EXTENSIONS = {".json", ".md", ".txt"}
COVER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_COMPRESSED = 100 * 1024 * 1024
MAX_UNCOMPRESSED = 300 * 1024 * 1024
MAX_FILES = 5000
MAX_RATIO = 200
MAX_COVER = 1_000_000
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTROL = re.compile(r"[\x00-\x1f\x7f]")
DRIVE = re.compile(r"^[A-Za-z]:")
DANGEROUS = re.compile(
    r"<\s*script|<\s*iframe|<\s*object|<\s*embed|javascript\s*:|data\s*:\s*text/html|"
    r"\bon(?:error|load|click|dblclick|mouse\w*|focus\w*|blur|key\w*|submit|change|input|toggle|pointer\w*|"
    r"animation\w*|transition\w*|begin|end|abort|unload)\s*=", re.IGNORECASE)
JUNK_NAMES = {"desktop.ini", ".ds_store", "thumbs.db", "_tarefas.md", "progress.json", ".env"}
JUNK_SUFFIXES = (".tmp", ".pyc")
JUNK_DIRS = {"__pycache__", ".git"}
FIXED_DATE = (2020, 1, 1, 0, 0, 0)
SPECS_FILES = ("CLAUDE.md", "docs/modelo-de-dados.md")


_IMPORT_LOCK = threading.Lock()      # importações simultâneas (mesmo slug) acontecem uma de cada vez


class PackageError(Exception):
    """Pacote recusado. `problems` lista, em português, tudo o que impediu."""

    def __init__(self, problems):
        self.problems = [problems] if isinstance(problems, str) else list(problems)
        super().__init__("; ".join(self.problems))


# ---- verificação do zip ------------------------------------------------------------------------------------------

def _is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return (mode & 0o170000) == 0o120000


def _check_name(name: str) -> str | None:
    """Motivo da recusa de um nome de entrada, ou None se estiver ok."""
    if CONTROL.search(name):
        return "byte de controle no nome"
    if "\\" in name:
        return "barra invertida no nome"
    if name.startswith("/") or DRIVE.match(name):
        return "caminho absoluto"
    parts = name.rstrip("/").split("/")
    if any(part in ("", ".", "..") for part in parts):
        return "caminho não normalizado (.. ou vazio)"
    return None


def _inspect_zip(archive: zipfile.ZipFile) -> tuple[str, list[zipfile.ZipInfo]]:
    """Valida nomes, tipos e limites. Devolve (slug, arquivos). Levanta PackageError com TODOS os problemas."""
    problems: list[str] = []
    infos = archive.infolist()
    if len(infos) > MAX_FILES + 1000:
        raise PackageError(f"entradas demais no pacote (máximo de {MAX_FILES} arquivos)")
    files = [i for i in infos if not i.is_dir()]
    if not files:
        raise PackageError("o pacote está vazio")
    if len(files) > MAX_FILES:
        problems.append(f"arquivos demais: {len(files)} (máximo {MAX_FILES})")
    tops, seen = set(), set()
    total = 0
    for info in infos:
        name = info.filename
        reason = _check_name(name)
        if reason:
            problems.append(f"entrada recusada ({reason}): {name!r}")
            continue
        top = name.split("/", 1)[0]
        tops.add(top)
        if _is_symlink(info):
            problems.append(f"link simbólico recusado: {name}")
            continue
        if info.is_dir():
            continue
        if "/" not in name:
            problems.append(f"arquivo fora da pasta da trilha: {name}")
            continue
        if info.flag_bits & 0x1:
            problems.append(f"arquivo criptografado recusado: {name}")
        suffix = PurePosixPath(name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            problems.append(f"extensão não permitida ({suffix or 'sem extensão'}): {name}")
        key = name.lower()
        if key in seen:
            problems.append(f"nome repetido (maiúsculas/minúsculas): {name}")
        seen.add(key)
        total += info.file_size
        if info.compress_size > 0 and info.file_size / info.compress_size > MAX_RATIO:
            problems.append(f"razão de compressão suspeita (possível zip bomb): {name}")
        elif info.compress_size == 0 and info.file_size > 1024:
            problems.append(f"razão de compressão suspeita (possível zip bomb): {name}")
    if total > MAX_UNCOMPRESSED:
        problems.append(f"conteúdo descompactado grande demais ({total // (1024 * 1024)} MB; máximo 300 MB)")
    if len(tops) != 1:
        problems.append("o pacote deve ter uma única pasta de topo <slug>/ (encontrei: "
                        + (", ".join(sorted(tops)) or "nenhuma") + ")")
        raise PackageError(problems)
    slug = next(iter(tops))
    if not SLUG.match(slug):
        problems.append(f"nome de pasta inválido para slug: {slug!r} (use só a-z, 0-9 e hífen)")
    if problems:
        raise PackageError(problems)
    return slug, files


def _extract(archive: zipfile.ZipFile, files: list, target_root: Path) -> None:
    """Extrai contando os bytes realmente lidos (não confia só nos tamanhos declarados)."""
    budget = MAX_UNCOMPRESSED
    root = target_root.resolve()
    for info in files:
        destination = (target_root / info.filename).resolve()
        if root not in destination.parents:
            raise PackageError(f"entrada tentou sair da pasta: {info.filename!r}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        written = 0
        with archive.open(info) as source, open(destination, "wb") as out:
            while True:
                chunk = source.read(65536)
                if not chunk:
                    break
                written += len(chunk)
                budget -= len(chunk)
                if written > info.file_size or budget < 0:
                    raise PackageError(f"conteúdo descompactado maior que o declarado em {info.filename}")
                out.write(chunk)


def _scan_content(folder: Path) -> list[str]:
    problems = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                problems.append(f"{path.relative_to(folder).as_posix()}: não é texto UTF-8")
                continue
            found = DANGEROUS.search(text)
            if found:
                problems.append(f"{path.relative_to(folder).as_posix()}: conteúdo perigoso "
                                f"({found.group(0).strip()[:20]!r}) não é permitido")
    return problems


def _check_manifest(folder: Path, slug: str) -> list[str]:
    import json
    try:
        manifest = json.loads((folder / "trail.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["trail.json ausente ou inválido"]
    if not isinstance(manifest, dict):
        return ["trail.json deve ser um objeto"]
    problems = []
    if manifest.get("id") != slug:
        problems.append(f"trail.json: id ({manifest.get('id')!r}) difere do nome da pasta ({slug!r})")
    cover = manifest.get("cover")
    if cover is not None:
        target = (folder / cover).resolve() if isinstance(cover, str) and cover and "\\" not in cover else None
        if target is None or folder.resolve() not in target.parents or not target.is_file():
            problems.append("trail.json: capa (cover) inválida ou inexistente")
        elif target.suffix.lower() not in COVER_EXTENSIONS:
            problems.append("trail.json: a capa deve ser png, jpg ou webp")
        elif target.stat().st_size > MAX_COVER:
            problems.append("trail.json: a capa passa de 1 MB")
    return problems


# ---- importar -----------------------------------------------------------------------------------------------------

def import_trail_zip(content_dir, data: bytes, replace: bool = False) -> dict:
    """Importa um pacote. Devolve {"slug", "warnings", "replaced"}; levanta PackageError(problems)."""
    with _IMPORT_LOCK:
        return _import_locked(Path(content_dir), data, replace)


def _import_locked(content_dir: Path, data: bytes, replace: bool) -> dict:
    if len(data) > MAX_COMPRESSED:
        raise PackageError("pacote maior que 100 MB")
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise PackageError("o arquivo não é um zip válido")
    with archive:
        slug, files = _inspect_zip(archive)
        final = content_dir / slug
        if final.exists() and not replace:
            raise PackageError(f"já existe uma trilha com o slug {slug!r}; peça a substituição (replace) para trocá-la")
        content_dir.mkdir(parents=True, exist_ok=True)
        temp = Path(tempfile.mkdtemp(prefix=".import-", dir=content_dir))
        backup = None
        try:
            try:
                _extract(archive, files, temp)
            except (zipfile.BadZipFile, zlib.error, EOFError, NotImplementedError, RuntimeError) as exc:
                raise PackageError(f"pacote corrompido ou não suportado ({type(exc).__name__})")
            folder = temp / slug
            problems = _check_manifest(folder, slug) + _scan_content(folder)
            if problems:
                raise PackageError(problems)
            _, found, warnings = validator.inspect(folder)
            if found:
                raise PackageError([f"validação: {p}" for p in found])
            replaced = final.exists()
            if replaced:
                backup = content_dir / f".backup-{slug}-{temp.name}"
                final.rename(backup)
            try:
                folder.rename(final)
            except OSError:
                if backup is not None and not final.exists():
                    backup.rename(final)
                    backup = None
                raise
            if backup is not None:
                shutil.rmtree(backup, ignore_errors=True)
            return {"slug": slug, "warnings": list(warnings), "replaced": replaced}
        finally:
            shutil.rmtree(temp, ignore_errors=True)


# ---- empacotar ----------------------------------------------------------------------------------------------------

def _is_junk(path: Path) -> bool:
    return (path.name.lower() in JUNK_NAMES or path.name.lower().endswith(JUNK_SUFFIXES)
            or any(part in JUNK_DIRS for part in path.parts))


def pack_trail(content_dir, slug: str, out_file) -> list[str]:
    """Valida a trilha e grava um zip determinístico `<slug>/...`. Devolve os avisos."""
    content_dir, out_file = Path(content_dir), Path(out_file)
    if not SLUG.match(slug) or not (content_dir / slug / "trail.json").is_file():
        raise PackageError(f"trilha não encontrada: {slug}")
    folder = content_dir / slug
    _, problems, warnings = validator.inspect(folder)
    if problems:
        raise PackageError([f"validação: {p}" for p in problems])
    entries = []
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        if path.is_symlink() or not path.is_file() or _is_junk(relative):
            continue
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise PackageError(f"extensão não permitida no pacote ({path.suffix or 'sem extensão'}): {relative.as_posix()}")
        entries.append((relative.as_posix(), path))
    entries.sort(key=lambda item: item[0])
    out_file.parent.mkdir(parents=True, exist_ok=True)
    temp = out_file.with_name(out_file.name + ".tmp")
    try:
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
            for relative, path in entries:
                info = zipfile.ZipInfo(f"{slug}/{relative}", FIXED_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())
        temp.replace(out_file)
    finally:
        temp.unlink(missing_ok=True)
    return list(warnings)


# ---- specs --------------------------------------------------------------------------------------------------------

def build_specs_zip(root) -> bytes:
    """Zip em memória com CLAUDE.md, specs/** e docs/modelo-de-dados.md (mesma estrutura de pastas)."""
    root = Path(root)
    wanted = []
    missing = []
    for name in SPECS_FILES:
        path = root / name
        (wanted if path.is_file() and not path.is_symlink() else missing).append((name, path))
    specs = root / "specs"
    if specs.is_dir() and not specs.is_symlink():
        for path in sorted(specs.rglob("*")):
            if path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents if root in p.parents):
                wanted.append((path.relative_to(root).as_posix(), path))
    else:
        missing.append(("specs/", specs))
    if missing:
        raise PackageError("faltam arquivos das specs em " + str(root) + ": " + ", ".join(n for n, _ in missing))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(wanted):
            info = zipfile.ZipInfo(name, FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return buffer.getvalue()
