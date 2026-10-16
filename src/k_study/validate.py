"""Validador de trilhas. Rode antes de dar um bloco por pronto:  kstudy validate [slug]

Verificações que tornam uma trilha INVÁLIDA (problemas), para cada bloco listado em trail.json:
  * trail.json: schema `trail/v1`, id igual ao nome da pasta, slug válido, título, blocos existentes,
    capa (cover) existente em png/jpg/webp de até 1 MB;
  * ids de itens únicos; tipos conhecidos; caminhos existem e ficam dentro da pasta da trilha;
  * imagens citadas em Markdown, enunciados e explicações existem;
  * vídeos: URL válida do YouTube; trechos com fim > início; transcrição existe quando citada;
  * questões: ids únicos; 'single' com exatamente 1 alternativa correta, 'multiple' com 2 ou mais;
    TODA alternativa tem explicação; toda questão tem generalExplanation;
  * nenhum caractere de controle deixado por escape quebrado no JSON (um "\\beta" que virou backspace).

Heurísticas que só AVISAM (nunca reprovam: olhe e decida):
  * trecho ou tempo de revisão além do fim do vídeo por mais que a tolerância (max(30 s, 5 %): o fim de um vídeo
    costuma ser música ou silêncio), ou trecho que começa muito depois da última fala;
  * LaTeX em Markdown ou questões (a interface não renderiza);
  * posição da resposta: maioria das 'single' na mesma letra, ou a correta quase sempre a mais longa;
  * explicações de alternativas muito curtas; leituras muito curtas.
"""
import json
import re
from pathlib import Path

ITEM_TYPES = {"video", "markdown", "pdf", "link", "questions"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
YOUTUBE = re.compile(r"(?:v=|youtu\.be/)([\w-]{11})")
LATEX = re.compile(r"\\(?:frac|text|sum|beta|alpha|hat|le|ge|leq|geq|times|cdot|bigcup|sqrt|lambda|mu|sigma)\b|"
                   r"(?<![A-Za-z0-9])\$[^\s$][^$\n]{0,60}\$(?![0-9])")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
CLOCK = re.compile(r"\b(\d{1,2}):(\d{2})\b")
TOLERANCE_SECONDS, TOLERANCE_FRACTION = 30, 0.05      # folga permitida além do fim do vídeo antes de avisar
SPOKEN_GAP_SECONDS = 90                               # trecho que começa tanto tempo depois da última fala


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def trail_slugs(content_dir: Path) -> list[str]:
    """Nomes das pastas de content/ que têm trail.json."""
    content_dir = Path(content_dir)
    if not content_dir.is_dir():
        return []
    return sorted(p.name for p in content_dir.iterdir() if p.is_dir() and (p / "trail.json").is_file())


def validate(trail_dir: Path) -> tuple[list[str], list[str]]:
    """Devolve (resumo, problemas). Veja `inspect` para os avisos também."""
    summary, problems, _ = inspect(trail_dir)
    return summary, problems


def inspect(trail_dir: Path) -> tuple[list[str], list[str], list[str]]:
    """Valida a pasta de UMA trilha. Devolve (resumo, problemas, avisos). Só os problemas reprovam."""
    data = Path(trail_dir).resolve()
    problems: list[str] = []
    warnings: list[str] = []
    latex_hits: dict[str, list[str]] = {}
    short_hits: dict[str, int] = {}

    def item_of(where: str) -> str:
        return "/".join(where.split("/")[:2])

    def inside(path: Path) -> bool:
        return data in path.resolve().parents

    def check_images(text: str, base: Path, where: str):
        for ref in IMAGE.findall(text or ""):
            if not ref.startswith("http") and not (base / ref).resolve().exists():
                problems.append(f"{where}: imagem não encontrada: {ref}")

    def check_text(text: str, where: str):
        if CONTROL.search(text or ""):
            problems.append(f"{where}: caractere de controle no texto (escape quebrado no JSON, como \\beta ou \\text)")
        found = LATEX.search(text or "")
        if found:
            latex_hits.setdefault(item_of(where), []).append(
                f"{where.split('/', 2)[-1] if where.count('/') > 1 else 'texto'} {found.group(0)[:24]!r}")

    def check_questions(path: Path, where: str) -> int:
        try:
            doc = _load(path)
            questions = doc["questions"]
            ids = [q["id"] for q in questions]
        except (ValueError, KeyError, TypeError) as exc:
            problems.append(f"{where}: arquivo de questões inválido ({type(exc).__name__}: {exc})")
            return 0
        if len(set(ids)) != len(ids):
            problems.append(f"{where}: ids de questão repetidos")
        singles, correct_at, longest = 0, {}, 0
        for q in questions:
            w = f"{where}/{q['id']}"
            try:
                options = q["options"]
                check_text(str(q.get("prompt", "")) + str(q.get("generalExplanation", "")), w)
                correct = sum(bool(o["correct"]) for o in options)
                if q["type"] == "single" and correct != 1:
                    problems.append(f"{w}: questão 'single' com {correct} alternativas corretas")
                elif q["type"] == "multiple" and correct < 2:
                    problems.append(f"{w}: questão 'multiple' com {correct} alternativas corretas")
                elif q["type"] not in ("single", "multiple"):
                    problems.append(f"{w}: tipo de questão desconhecido: {q['type']}")
                if q["type"] == "single" and correct == 1:
                    at = next(i for i, o in enumerate(options) if o["correct"])
                    singles += 1
                    correct_at[at] = correct_at.get(at, 0) + 1
                    lengths = [len(str(o.get("text", ""))) for o in options]
                    longest += lengths[at] == max(lengths)
                for o in options:
                    check_text(str(o.get("text", "")) + str(o.get("explanation", "")), f"{w}/{o['id']}")
                    explanation = str(o.get("explanation", "")).strip()
                    if not explanation:
                        problems.append(f"{w}/{o['id']}: alternativa sem explicação")
                    elif len(explanation) < 40:
                        short_hits[item_of(w)] = short_hits.get(item_of(w), 0) + 1
                if not q.get("generalExplanation"):
                    problems.append(f"{w}: falta generalExplanation")
                prompt = q.get("prompt", "")
                if q.get("promptFile"):
                    pf = path.parent / q["promptFile"]
                    if not pf.exists():
                        problems.append(f"{w}: promptFile não encontrado")
                    else:
                        prompt = pf.read_text(encoding="utf-8")
                check_images(prompt, path.parent, w)
                check_images(q.get("generalExplanation", ""), path.parent, w)
                for o in options:
                    check_images(o.get("explanation", ""), path.parent, w)
            except (KeyError, TypeError) as exc:
                problems.append(f"{w}: questão malformada (faltando {exc})")
        if singles >= 6:
            letter, count = max(correct_at.items(), key=lambda kv: kv[1])
            if count / singles > 0.6:
                warnings.append(f"{where}: {count} de {singles} respostas 'single' estão na alternativa {'ABCDEFGH'[letter]}; embaralhe as alternativas")
            if longest / singles > 0.7:
                warnings.append(f"{where}: a alternativa correta é a mais longa em {longest} de {singles} questões 'single'; equilibre os tamanhos")
        return len(questions)

    def check_video_times(item: dict, transcript: dict, w: str):
        segments = transcript.get("segments") or []
        duration = transcript.get("duration") or (segments[-1][0] if segments else 0)
        if not duration:
            return
        slack = max(TOLERANCE_SECONDS, TOLERANCE_FRACTION * duration)
        last_spoken = segments[-1][0] if segments else duration
        for clip in item.get("clips", []):
            if clip["start"] >= duration:
                warnings.append(f"{w}: o trecho {clip['start']}-{clip['end']} s começa depois do fim do vídeo ({duration} s)")
            elif clip["end"] > duration + slack:
                warnings.append(f"{w}: o trecho {clip['start']}-{clip['end']} s termina {clip['end'] - duration:.0f} s além do fim do vídeo ({duration} s)")
            elif clip["start"] > last_spoken + SPOKEN_GAP_SECONDS:
                warnings.append(f"{w}: o trecho começa em {clip['start']} s mas a última fala está em {last_spoken} s")
        for line in (item.get("review") or {}).get("covers", []):
            for minutes, seconds in CLOCK.findall(line):
                if int(minutes) * 60 + int(seconds) > duration + slack:
                    warnings.append(f"{w}: a revisão cita {minutes}:{seconds} mas o vídeo dura {int(duration) // 60}:{int(duration) % 60:02d}")
                    break

    summary: list[str] = []
    try:
        manifest = _load(data / "trail.json")
        if not isinstance(manifest, dict) or not isinstance(manifest.get("blocks"), list):
            raise TypeError("o trail.json deve ser um objeto com a lista 'blocks'")
        blocks = manifest["blocks"]
    except FileNotFoundError:
        return summary, [f"trail.json não encontrado em {data.name}/"], warnings
    except (ValueError, TypeError) as exc:
        return summary, [f"trail.json inválido ({type(exc).__name__}: {exc})"], warnings
    if manifest.get("schema") != "trail/v1":
        problems.append(f"trail.json: schema deve ser 'trail/v1' (está {manifest.get('schema')!r})")
    if manifest.get("id") != data.name:
        problems.append(f"trail.json: id ({manifest.get('id')!r}) difere do nome da pasta ({data.name!r})")
    if not SLUG.match(data.name):
        problems.append(f"slug inválido: {data.name!r} (use só a-z, 0-9 e hífen)")
    if not str(manifest.get("title") or "").strip():
        problems.append("trail.json: falta o título (title)")
    cover = manifest.get("cover")
    if cover is not None:
        target = (data / cover).resolve() if isinstance(cover, str) and cover and "\\" not in cover else None
        if target is None or data not in target.parents:
            problems.append("trail.json: a capa (cover) deve ser um caminho relativo dentro da pasta da trilha")
        elif not target.is_file():
            problems.append(f"trail.json: capa não encontrada: {cover}")
        elif target.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            problems.append("trail.json: a capa deve ser png, jpg ou webp")
        elif target.stat().st_size > 1_000_000:
            problems.append("trail.json: a capa passa de 1 MB")
    seen_blocks = set()
    for entry in blocks:
        if not isinstance(entry, dict) or not entry.get("id") or not entry.get("file"):
            problems.append(f"trail.json: bloco malformado: {entry!r}")
            continue
        if entry["id"] in seen_blocks:
            problems.append(f"trail.json: id de bloco repetido: {entry['id']}")
        seen_blocks.add(entry["id"])
        block_path = (data / entry["file"]).resolve()
        if not inside(block_path):
            problems.append(f"{entry['id']}: o arquivo do bloco sai da pasta da trilha")
            continue
        if not block_path.is_file():
            problems.append(f"{entry['id']}: arquivo do bloco não encontrado: {entry['file']}")
            continue
        try:
            block = _load(block_path)
            sections = block["sections"]
            block_id = block["id"]
        except (ValueError, KeyError, TypeError) as exc:
            problems.append(f"{entry['id']}: block.json inválido ({type(exc).__name__}: {exc})")
            continue
        if block_id != entry["id"]:
            problems.append(f"{entry['id']}: o id do block.json ({block_id}) difere do trail.json")
        seen, n_questions, n_videos = set(), 0, 0
        for section in sections:
            for item in section.get("items", []):
                try:
                    w = f"{block_id}/{item['id']}"
                    kind = item["type"]
                except (KeyError, TypeError):
                    problems.append(f"{block_id}: item sem id ou sem type: {item!r}")
                    continue
                if item["id"] in seen:
                    problems.append(f"{w}: id de item repetido")
                seen.add(item["id"])
                if kind not in ITEM_TYPES:
                    problems.append(f"{w}: tipo desconhecido: {kind}")
                if "path" in item:
                    target = (block_path.parent / item["path"]).resolve()
                    if not inside(target):
                        problems.append(f"{w}: o caminho sai da pasta da trilha")
                    elif not target.exists():
                        problems.append(f"{w}: arquivo não encontrado: {item['path']}")
                    elif kind == "questions":
                        n_questions += check_questions(target, w)
                    elif kind == "markdown":
                        text = target.read_text(encoding="utf-8")
                        check_images(text, target.parent, w)
                        check_text(text, w)
                        name = item["path"].lower()
                        if text.count("\n") < 250 and "guia" not in name and "guide" not in name:
                            warnings.append(f"{w}: leitura curta ({text.count(chr(10))} linhas; o alvo é de 350 a 700)")
                if kind == "video":
                    n_videos += 1
                    if not YOUTUBE.search(item.get("url", "")):
                        problems.append(f"{w}: URL de vídeo inválida")
                    if item.get("transcript"):
                        t = (block_path.parent / item["transcript"]).resolve()
                        if not inside(t) or not t.exists():
                            problems.append(f"{w}: transcrição não encontrada: {item['transcript']}")
                        else:
                            try:
                                check_video_times(item, _load(t), w)
                            except (ValueError, KeyError, TypeError) as exc:
                                problems.append(f"{w}: transcrição ilegível ({type(exc).__name__}: {exc})")
                    if item.get("review") and not item.get("transcript"):
                        problems.append(f"{w}: tem revisão mas não tem transcrição")
                    for clip in item.get("clips", []):
                        if clip["end"] <= clip["start"]:
                            problems.append(f"{w}: trecho com fim <= início")
        summary.append(f"{block_id}: {len(seen)} itens, {n_videos} vídeos, {n_questions} questões")
    for where, hits in latex_hits.items():
        warnings.append(f"{where}: {len(hits)} trecho(s) parecem LaTeX (ex.: {hits[0]}); a interface não renderiza, use Unicode")
    for where, count in short_hits.items():
        warnings.append(f"{where}: {count} explicação(ões) de alternativa com menos de 40 caracteres")
    return summary, problems, warnings
