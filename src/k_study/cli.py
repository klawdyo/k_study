"""Linha de comando do k_study:  kstudy <comando>   (ou  py main.py <comando>;  sem comando = serve)

  serve            sobe o servidor (alunos em /, administração em /admin/; porta 8765)
  validate [slug]  valida a estrutura de uma trilha (ou de todas); erros reprovam, heurísticas só avisam
  sync             reindexa content/ no banco
  trails           lista as trilhas e seus números
  new-trail SLUG   cria content/<slug>/ com trail.json e a estrutura mínima
  pack SLUG        valida e gera o pacote zip importável de uma trilha
  import-trail ZIP importa um pacote zip de trilha (mesma rotina do upload do admin)
  set-admin EMAIL  torna uma conta existente administradora (recuperação)
  reset-password EMAIL  define uma nova senha (pedida no terminal, sem eco)
  import-progress  importa um progress.json antigo para uma conta existente

Códigos de saída: 0 ok, 1 problemas de validação, 2 erro de uso ou de ambiente.
Pasta de conteúdo: --content-dir ou K_STUDY_CONTENT (padrão ./content). Banco: --db ou K_STUDY_DB (padrão ./data/k_study.db).
Segredos: --env ou K_STUDY_ENV (padrão ./.env).
"""
import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

from . import __version__


# mensagens automáticas do argparse em português (o módulo as busca por gettext em inglês)
_PTBR = {
    "usage: ": "uso: ", "positional arguments": "argumentos posicionais", "options": "opções", "optional arguments": "opções",
    "show this help message and exit": "mostra esta ajuda e sai",
    "%(prog)s: error: %(message)s\n": "%(prog)s: erro: %(message)s\n",
    "the following arguments are required: %s": "os argumentos a seguir são obrigatórios: %s",
    "unrecognized arguments: %s": "argumentos não reconhecidos: %s",
    "expected one argument": "esperava um argumento", "expected at least one argument": "esperava ao menos um argumento",
    "argument %(argument_name)s: %(message)s": "argumento %(argument_name)s: %(message)s",
    "invalid %(type)s value: %(value)r": "valor inválido para %(type)s: %(value)r",
    "invalid choice: %(value)r (choose from %(choices)s)": "opção inválida: %(value)r (escolha entre %(choices)s)",
    "invalid choice: %(value)r (choose from %(choices)s)": "opção inválida: %(value)r (escolha entre %(choices)s)",
}
argparse._ = lambda text: _PTBR.get(text, text)

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COMMANDS = ("serve", "validate", "sync", "trails", "new-trail", "pack", "import-trail", "set-admin",
            "reset-password", "import-progress")


class UsageError(Exception):
    """Erro de uso ou de ambiente (código de saída 2)."""


def _stdout_utf8():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", line_buffering=True)
        except Exception:
            pass


def content_dir_of(args) -> Path:
    return Path(args.content_dir or os.environ.get("K_STUDY_CONTENT") or "content")


def db_path_of(args) -> Path:
    from .db import default_db_path
    return default_db_path(args.db)


def env_path_of(args) -> Path:
    return Path(getattr(args, "env", None) or os.environ.get("K_STUDY_ENV") or ".env")


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--content-dir", metavar="PASTA", help="pasta com as trilhas (padrão: $K_STUDY_CONTENT ou ./content)")
    common.add_argument("--db", metavar="ARQUIVO", help="arquivo do banco SQLite (padrão: $K_STUDY_DB ou ./data/k_study.db)")
    common.add_argument("--env", metavar="ARQUIVO", help="arquivo .env com o segredo (padrão: $K_STUDY_ENV ou ./.env)")

    ap = argparse.ArgumentParser(prog="kstudy", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                 add_help=False)
    ap.add_argument("-h", "--help", action="help", help="mostra esta ajuda e sai")
    ap.add_argument("--version", action="version", version=f"k_study {__version__}", help="mostra a versão e sai")
    sub = ap.add_subparsers(dest="command", metavar="comando")

    def add(name, help_text, parents=(common,)):
        p = sub.add_parser(name, help=help_text, description=help_text, parents=list(parents), add_help=False)
        p.add_argument("-h", "--help", action="help", help="mostra esta ajuda e sai")
        return p

    s = add("serve", "sobe o servidor dos alunos")
    s.add_argument("--port", type=int, default=8765, help="porta (padrão 8765)")
    s.add_argument("--host", metavar="ENDEREÇO", default=None,
                   help="endereço em que escuta (padrão: 127.0.0.1, ou $K_STUDY_HOST); em Docker use 0.0.0.0")
    s.add_argument("--lan", action="store_true",
                   help="aceita também outros computadores da sua rede privada (o firewall pode pedir permissão)")

    s = add("validate", "valida uma trilha (ou todas)")
    s.add_argument("slug", nargs="?", help="trilha a validar (padrão: todas)")

    s = add("sync", "reindexa o conteúdo no banco")
    s.add_argument("--force", action="store_true", help="reindexa todas as trilhas, mesmo sem mudança nos manifestos")

    add("trails", "lista as trilhas e seus números")

    s = add("new-trail", "cria uma trilha nova com a estrutura mínima")
    s.add_argument("slug", help="identificador da trilha e nome da pasta: só a-z, 0-9 e hífen")
    s.add_argument("--title", required=True, help="título da trilha")
    s.add_argument("--description", default="", help="descrição curta")

    s = add("pack", "valida e gera o pacote zip importável de uma trilha")
    s.add_argument("slug", help="trilha a empacotar")
    s.add_argument("--out", metavar="ARQUIVO", help="arquivo de saída (padrão: <slug>.zip na pasta atual)")

    s = add("import-trail", "importa um pacote zip de trilha")
    s.add_argument("file", metavar="ARQUIVO.zip", help="pacote da trilha")
    s.add_argument("--replace", action="store_true", help="troca a trilha se o slug já existir (o progresso é mantido)")

    s = add("set-admin", "torna uma conta existente administradora")
    s.add_argument("email", help="e-mail da conta")

    s = add("reset-password", "define uma nova senha para uma conta existente")
    s.add_argument("email", help="e-mail da conta")

    s = add("import-progress", "importa um progress.json antigo para uma conta existente")
    s.add_argument("file", metavar="ARQUIVO.json", help="progress.json antigo (não é alterado)")
    s.add_argument("--email", required=True, help="e-mail da conta (ela precisa existir)")
    s.add_argument("--trail", required=True, metavar="SLUG", help="trilha que recebe o progresso")
    return ap


# ---- comandos ------------------------------------------------------------------------------------------------------

def cmd_serve(args) -> int:
    from .server import serve
    serve(content_dir_of(args), db_path_of(args), args.port, args.lan, env_path_of(args),
          args.host or os.environ.get("K_STUDY_HOST") or "127.0.0.1")
    return 0


def cmd_validate(args) -> int:
    from .validate import inspect, trail_slugs
    content = content_dir_of(args)
    slugs = trail_slugs(content)
    if args.slug:
        if not (content / args.slug / "trail.json").is_file():
            raise UsageError(f"trilha não encontrada: {content / args.slug}")
        slugs = [args.slug]
    if not slugs:
        print(f"Nenhuma trilha encontrada em {content}.")
        return 0
    failed = False
    for slug in slugs:
        summary, problems, warnings = inspect(content / slug)
        print(f"== {slug}")
        print("\n".join(summary))
        print("PROBLEMAS:" if problems else "OK: nenhum problema.")
        for p in problems:
            print(" -", p)
        if warnings:
            print(f"AVISOS ({len(warnings)}; heurísticas, nunca reprovam a validação; confira):")
            for w in warnings:
                print(" ~", w)
        failed = failed or bool(problems)
    return 1 if failed else 0


def cmd_sync(args) -> int:
    from .db import Database
    from .indexer import sync
    result = sync(content_dir_of(args), Database(db_path_of(args)), force=args.force)
    print(f"Reindexadas: {', '.join(result['indexed']) or 'nenhuma (nada mudou)'}")
    if result["removed"]:
        print(f"Removidas do índice (pasta sumiu): {', '.join(result['removed'])}")
    for slug, reason in result["skipped"].items():
        print(f"aviso: trilha {slug} ignorada: {reason}", file=sys.stderr)
    return 0


def cmd_trails(args) -> int:
    from .db import Database
    from .indexer import sync
    db = Database(db_path_of(args))
    sync(content_dir_of(args), db)
    rows = db.list_trails()
    if not rows:
        print(f"Nenhuma trilha em {content_dir_of(args)}. Crie uma com: kstudy new-trail SLUG --title \"Título\"")
        return 0
    width = max(len(r["slug"]) for r in rows)
    for r in rows:
        print(f"{r['slug']:<{width}}  {r['blocks']} blocos, {r['items']} itens ({r['requiredItems']} obrigatórios), "
              f"~{r['minutes']} min  |  {r['title']}")
    return 0


def cmd_new_trail(args) -> int:
    from .db import now
    slug = args.slug
    if not SLUG.match(slug):
        raise UsageError(f"slug inválido: {slug!r}. Use só a-z, 0-9 e hífen, sem começar nem terminar com hífen.")
    folder = content_dir_of(args) / slug
    if folder.exists():
        raise UsageError(f"já existe: {folder}")
    manifest = {"schema": "trail/v1", "id": slug, "title": args.title, "description": args.description,
                "language": "pt-BR", "level": "iniciante", "tags": [], "createdAt": date.today().isoformat(),
                "blocks": [{"id": "block-1", "title": "Bloco 1", "file": "block-1/block.json"}]}
    block = {"schema": "block/v2", "id": "block-1", "title": "Bloco 1", "description": "", "sections": []}
    (folder / "block-1").mkdir(parents=True)
    for name in ("transcripts", "figures"):
        (folder / name).mkdir()
        (folder / name / ".gitkeep").write_text("", encoding="utf-8")
    (folder / "trail.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (folder / "block-1" / "block.json").write_text(json.dumps(block, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Trilha criada em {folder}\nPróximo passo: preencha block-1/block.json e rode `kstudy validate {slug}`.")
    return 0


def _packages():
    try:
        from . import packages
    except ImportError:
        raise UsageError("o módulo de pacotes (k_study.packages) ainda não está instalado neste projeto.")
    return packages


def cmd_pack(args) -> int:
    packages = _packages()
    out = Path(args.out) if args.out else Path(f"{args.slug}.zip")
    try:
        warnings = packages.pack_trail(content_dir_of(args), args.slug, out)
    except packages.PackageError as exc:
        print("PROBLEMAS:", file=sys.stderr)
        for problem in exc.problems:
            print(" -", problem, file=sys.stderr)
        return 1
    for warning in warnings:
        print(" ~", warning)
    print(f"Pacote gerado: {out.resolve()}")
    return 0


def cmd_import_trail(args) -> int:
    from .db import Database
    from .indexer import sync
    packages = _packages()
    source = Path(args.file)
    try:
        data = source.read_bytes()
    except OSError as exc:
        raise UsageError(f"não consegui ler {source}: {exc.strerror or exc}")
    try:
        result = packages.import_trail_zip(content_dir_of(args), data, replace=args.replace)
    except packages.PackageError as exc:
        print("O pacote foi recusado:", file=sys.stderr)
        for problem in exc.problems:
            print(" -", problem, file=sys.stderr)
        return 1
    sync(content_dir_of(args), Database(db_path_of(args)), force=True)
    for warning in result.get("warnings", []):
        print(" ~", warning)
    print(f"Trilha {result['slug']} {'substituída' if result.get('replaced') else 'importada'}.")
    return 0


def _existing_student(args):
    from .db import Database, normalize_email
    email = normalize_email(args.email)
    if email is None:
        raise UsageError(f"e-mail inválido: {args.email!r}")
    db = Database(db_path_of(args))
    row = db.find_student(email)
    if row is None:
        raise UsageError(f"não existe conta com o e-mail {email}. A pessoa precisa se cadastrar na interface primeiro.")
    return db, row


def cmd_set_admin(args) -> int:
    db, row = _existing_student(args)
    db.set_admin(row["id"], True)
    db.audit(row["id"], "set_admin", "pela linha de comando")
    print(f"{row['email']} agora é administradora.")
    return 0


def cmd_reset_password(args) -> int:
    import getpass
    from . import security
    db, row = _existing_student(args)
    secret = security.ensure_secret(env_path_of(args))
    first = getpass.getpass("Nova senha: ")
    problem = security.check_password_policy(first, row["email"])
    if problem:
        raise UsageError(problem)
    if getpass.getpass("Repita a nova senha: ") != first:
        raise UsageError("a confirmação não confere; nada foi alterado.")
    db.set_credentials(row["id"], None, security.hash_password(first, secret))
    db.run("DELETE FROM sessions WHERE student_id=?", (row["id"],))
    db.audit(row["id"], "reset_password", "pela linha de comando")
    print(f"Senha de {row['email']} redefinida; as sessões abertas foram encerradas.")
    return 0


def cmd_import_progress(args) -> int:
    from .db import Database, normalize_email
    from .indexer import sync
    email = normalize_email(args.email)
    if email is None:
        raise UsageError(f"e-mail inválido: {args.email!r}")
    source = Path(args.file)
    try:
        state = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise UsageError(f"não consegui ler {source}: {exc.strerror or exc}")
    except ValueError as exc:
        raise UsageError(f"{source} não é um JSON válido: {exc}")
    if not isinstance(state, dict) or not any(k in state for k in ("items", "answers", "notes")):
        raise UsageError(f"{source} não parece um progress.json (esperava as chaves items, answers e notes).")
    db = Database(db_path_of(args))
    sync(content_dir_of(args), db)
    if not db.trail_exists(args.trail):
        raise UsageError(f"trilha não encontrada: {args.trail}")
    row = db.find_student(email)
    if row is None:
        raise UsageError(f"não existe conta com o e-mail {email}. Cadastre-se na interface e rode o comando de novo.")
    student, created = {"id": row["id"], "email": row["email"]}, False
    counts = db.import_state(student["id"], args.trail, state)
    known = {(r["block_id"], r["item_id"]) for r in db.query("SELECT block_id, item_id FROM items WHERE trail=?", (args.trail,))}
    keys = set(state.get("items") or {}) | set(state.get("answers") or {}) | set(state.get("notes") or {})
    unknown = sorted(k for k in keys if tuple(k.split("/", 1)) not in known)
    print(f"Conta {email}. Importados: {counts['items']} itens, "
          f"{counts['answers']} respostas, {counts['notes']} anotações; ignorados por formato inválido: {counts['skipped']}.")
    if unknown:
        print(f"aviso: {len(unknown)} chave(s) não existem hoje na trilha (ficam guardadas): {', '.join(unknown[:5])}"
              f"{' ...' if len(unknown) > 5 else ''}", file=sys.stderr)
    return 0


HANDLERS = {"serve": cmd_serve, "validate": cmd_validate, "sync": cmd_sync, "trails": cmd_trails,
            "new-trail": cmd_new_trail, "pack": cmd_pack, "import-trail": cmd_import_trail, "set-admin": cmd_set_admin,
            "reset-password": cmd_reset_password, "import-progress": cmd_import_progress}


def main(argv=None) -> int:
    _stdout_utf8()
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or (argv[0].startswith("-") and argv[0] not in ("-h", "--help", "--version")):
        argv.insert(0, "serve")                       # sem comando = serve (aceita `py main --lan`)
    args = build_parser().parse_args(argv)
    if not args.command:
        build_parser().print_help()
        return 0
    try:
        return HANDLERS[args.command](args)
    except UsageError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 0
    except OSError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
