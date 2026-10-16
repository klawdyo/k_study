import json
import subprocess
import sys
from pathlib import Path

from k_study.cli import main
from k_study.db import Database

ROOT = Path(__file__).resolve().parent.parent


def run(capsys, tmp_path, *args, content=None, db=True):
    argv = list(args)
    if content is not False:
        argv += ["--content-dir", str(content or tmp_path / "content")]
    if db:
        argv += ["--db", str(tmp_path / "data" / "k_study.db")]
    code = main(argv)
    out = capsys.readouterr()
    return code, out.out, out.err


def test_new_trail_cria_estrutura_valida(capsys, tmp_path):
    code, out, _ = run(capsys, tmp_path, "new-trail", "minha-trilha", "--title", "Minha trilha", "--description", "Descrição", db=False)
    assert code == 0 and "Trilha criada" in out
    folder = tmp_path / "content" / "minha-trilha"
    manifest = json.loads((folder / "trail.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "trail/v1" and manifest["id"] == "minha-trilha" and manifest["title"] == "Minha trilha"
    assert manifest["description"] == "Descrição" and manifest["blocks"][0]["file"] == "block-1/block.json"
    assert (folder / "block-1" / "block.json").is_file() and (folder / "transcripts").is_dir() and (folder / "figures").is_dir()
    code, out, _ = run(capsys, tmp_path, "validate", "minha-trilha", db=False)
    assert code == 0 and "OK: nenhum problema." in out


def test_new_trail_recusa_slug_ruim_e_pasta_existente(capsys, tmp_path):
    for slug in ("Maiúscula", "com espaço", "x-", "a--b", "../fora"):
        code, _, err = run(capsys, tmp_path, "new-trail", slug, "--title", "T", db=False)
        assert code == 2 and "slug inválido" in err, slug
    assert not (tmp_path / "fora").exists()
    assert run(capsys, tmp_path, "new-trail", "ok", "--title", "T", db=False)[0] == 0
    code, _, err = run(capsys, tmp_path, "new-trail", "ok", "--title", "T", db=False)
    assert code == 2 and "já existe" in err


def test_validate_codigos_de_saida(capsys, tmp_path, content, trail_dir):
    code, out, _ = run(capsys, tmp_path, "validate", content=content, db=False)
    assert code == 0 and "== demo" in out and "block-1: 3 itens" in out
    (trail_dir / "block-1" / "read.md").unlink()
    code, out, _ = run(capsys, tmp_path, "validate", "demo", content=content, db=False)
    assert code == 1 and "PROBLEMAS:" in out and "arquivo não encontrado" in out
    code, _, err = run(capsys, tmp_path, "validate", "nada", content=content, db=False)
    assert code == 2 and "trilha não encontrada" in err


def test_validate_sem_trilhas(capsys, tmp_path):
    code, out, _ = run(capsys, tmp_path, "validate", db=False)
    assert code == 0 and "Nenhuma trilha" in out


def test_sync_e_trails(capsys, tmp_path, content):
    code, out, _ = run(capsys, tmp_path, "sync", content=content)
    assert code == 0 and "demo" in out
    code, out, _ = run(capsys, tmp_path, "sync", content=content)
    assert "nenhuma" in out
    code, out, _ = run(capsys, tmp_path, "trails", content=content)
    assert code == 0 and out.startswith("demo") and "1 blocos, 3 itens (2 obrigatórios)" in out
    import shutil
    shutil.rmtree(content / "demo")
    code, out, _ = run(capsys, tmp_path, "sync", content=content)
    assert "Removidas do índice" in out and "demo" in out
    assert "Nenhuma trilha" in run(capsys, tmp_path, "trails", content=content)[1]


def test_variaveis_de_ambiente_definem_conteudo_e_banco(capsys, tmp_path, content, monkeypatch):
    monkeypatch.setenv("K_STUDY_CONTENT", str(content))
    monkeypatch.setenv("K_STUDY_DB", str(tmp_path / "x" / "outro.db"))
    code = main(["trails"])
    assert code == 0 and "demo" in capsys.readouterr().out
    assert (tmp_path / "x" / "outro.db").exists()


def old_progress():
    return {"items": {"block-1/r": {"done": True, "at": "2026-10-01T10:00:00+00:00"}, "block-1/zzz": {"done": True}},
            "answers": {"block-1/q": {"q01": {"chosen": ["a"], "correct": True, "at": "2026-10-01T10:05:00+00:00"}}},
            "notes": {"block-1/r": "minha nota"}}


def test_import_progress(capsys, tmp_path, content):
    source = tmp_path / "progress.json"
    source.write_text(json.dumps(old_progress()), encoding="utf-8")
    before = source.read_bytes()
    code, _, err = run(capsys, tmp_path, "import-progress", "--email", "ana@exemplo.com", "--trail", "demo", str(source),
                       content=content)
    assert code == 2 and "não existe conta" in err                       # a conta precisa existir
    db = Database(tmp_path / "data" / "k_study.db")
    db.create_student("ana@exemplo.com", "Ana", "x")
    db.close()
    code, out, err = run(capsys, tmp_path, "import-progress", "--email", "Ana@Exemplo.com", "--trail", "demo", str(source), content=content)
    assert code == 0 and "Conta ana@exemplo.com" in out and "2 itens, 1 respostas, 1 anotações" in out
    assert "block-1/zzz" in err                       # item que não existe mais: só avisa
    assert source.read_bytes() == before              # o arquivo de origem não é alterado
    db = Database(tmp_path / "data" / "k_study.db")
    student = db.one("SELECT id FROM students WHERE email='ana@exemplo.com'")
    state = db.progress_state(student["id"], "demo")
    assert state["items"]["block-1/r"] == {"done": True, "at": "2026-10-01T10:00:00+00:00"}
    assert state["answers"]["block-1/q"]["q01"]["chosen"] == ["a"] and state["notes"]["block-1/r"] == "minha nota"
    db.close()
    code, out, _ = run(capsys, tmp_path, "import-progress", "--email", "ana@exemplo.com", "--trail", "demo", str(source), content=content)
    assert code == 0 and "2 itens" in out          # reimportar é idempotente


def test_import_progress_erros(capsys, tmp_path, content):
    source = tmp_path / "p.json"
    source.write_text(json.dumps(old_progress()), encoding="utf-8")
    base = ["import-progress", "--email", "ana@exemplo.com", "--trail", "demo"]
    assert "e-mail inválido" in run(capsys, tmp_path, "import-progress", "--email", "x", "--trail", "demo", str(source), content=content)[2]
    assert "trilha não encontrada" in run(capsys, tmp_path, "import-progress", "--email", "a@b.co", "--trail", "nada", str(source), content=content)[2]
    assert run(capsys, tmp_path, *base, str(tmp_path / "nao-existe.json"), content=content)[0] == 2
    source.write_text("{quebrado", encoding="utf-8")
    assert "JSON válido" in run(capsys, tmp_path, *base, str(source), content=content)[2]
    source.write_text('{"outra": 1}', encoding="utf-8")
    assert "não parece um progress.json" in run(capsys, tmp_path, *base, str(source), content=content)[2]


def test_comando_admin_nao_existe_mais(capsys, tmp_path):
    try:
        main(["admin"])
    except SystemExit as exc:
        assert exc.code == 2
    assert "admin" not in capsys.readouterr().out


def test_set_admin_e_reset_password(capsys, tmp_path, monkeypatch):
    from k_study import security
    env = tmp_path / ".env"
    db = Database(tmp_path / "data" / "k_study.db")
    secret = security.ensure_secret(env)
    db.create_student("primeira@exemplo.com", "P", "x")
    student, _ = db.create_student("ana@exemplo.com", "Ana", "x")
    db.create_session(student["id"], "tok", "csrf")
    db.close()
    base = ["--db", str(tmp_path / "data" / "k_study.db"), "--env", str(env)]
    assert main(["set-admin", "nao@existe.com", *base]) == 2
    assert "não existe conta" in capsys.readouterr().err
    assert main(["set-admin", "ANA@exemplo.com", *base]) == 0
    answers = iter(["nova-senha-12", "nova-senha-12"])
    monkeypatch.setattr("getpass.getpass", lambda prompt="": next(answers))
    assert main(["reset-password", "ana@exemplo.com", *base]) == 0
    capsys.readouterr()
    db = Database(tmp_path / "data" / "k_study.db")
    row = db.find_student("ana@exemplo.com")
    assert row["is_admin"] == 1 and security.verify_password("nova-senha-12", row["password_hash"], secret)
    assert db.one("SELECT COUNT(*) AS n FROM sessions")["n"] == 0
    answers = iter(["nova-senha-12", "diferente-123"])
    assert main(["reset-password", "ana@exemplo.com", *base]) == 2
    assert "confirmação" in capsys.readouterr().err


def test_pack_e_import_trail_usam_packages(capsys, tmp_path, content, monkeypatch):
    import sys
    import types
    calls = []
    fake = types.ModuleType("k_study.packages")

    class PackageError(Exception):
        problems = ["falha"]

    fake.PackageError = PackageError
    fake.pack_trail = lambda content_dir, slug, out: calls.append(("pack", slug, out)) or ["um aviso"]
    fake.import_trail_zip = lambda content_dir, data, replace=False: calls.append(("import", data, replace)) or {
        "slug": "demo", "warnings": [], "replaced": replace}
    monkeypatch.setitem(sys.modules, "k_study.packages", fake)
    import k_study
    monkeypatch.setattr(k_study, "packages", fake, raising=False)
    out_zip = tmp_path / "demo.zip"
    assert run(capsys, tmp_path, "pack", "demo", "--out", str(out_zip), content=content)[0] == 0
    out_zip.write_bytes(b"zip")
    code, out, _ = run(capsys, tmp_path, "import-trail", str(out_zip), "--replace", content=content)
    assert code == 0 and "substituída" in out
    assert calls == [("pack", "demo", out_zip), ("import", b"zip", True)]


def test_ajuda_em_portugues(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    out = capsys.readouterr().out
    assert "sobe o servidor" in out and "mostra esta ajuda" in out and "set-admin" in out


def test_sem_comando_equivale_a_serve(monkeypatch):
    calls = []
    import k_study.server as server_module
    monkeypatch.setattr(server_module, "serve", lambda *a: calls.append(a))
    assert main([]) == 0
    assert main(["--lan", "--port", "1234"]) == 0
    assert calls[0][2:4] == (8765, False) and calls[1][2:4] == (1234, True)


def test_main_py_roda_sem_instalar():
    done = subprocess.run([sys.executable, str(ROOT / "main.py"), "--help"], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(ROOT.parent))
    assert done.returncode == 0 and "serve" in done.stdout
