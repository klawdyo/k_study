import io
import json
import os
import zipfile
from pathlib import Path

import pytest

from conftest import make_trail
from k_study import packages
from k_study.packages import PackageError, build_specs_zip, import_trail_zip, pack_trail
from k_study.validate import validate

ROOT = Path(__file__).resolve().parent.parent


def build(entries, symlinks=()):
    """Monta um zip em memória. entries: {nome: bytes|str}; symlinks: nomes que viram link simbólico."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            data = content.encode("utf-8") if isinstance(content, str) else content
            info = zipfile.ZipInfo(name)
            info.filename = name                      # ZipInfo normaliza; aqui queremos o nome cru
            info.compress_type = zipfile.ZIP_DEFLATED
            if name in symlinks:
                info.external_attr = (0o120777 << 16)
            archive.writestr(info, data)
    return buffer.getvalue()


def trail_files(tmp_path, slug="novo"):
    """Arquivos {caminho-no-zip: bytes} de uma trilha válida."""
    source = tmp_path / "origem"
    make_trail(source, slug, "Nova")
    return {f"{slug}/{p.relative_to(source / slug).as_posix()}": p.read_bytes()
            for p in sorted((source / slug).rglob("*")) if p.is_file()}


def no_trash(content):
    """Nada além das trilhas deve sobrar no content/."""
    return sorted(p.name for p in content.iterdir()) if content.exists() else []


def refuse(content, data, *needles, replace=False):
    before = no_trash(content)
    with pytest.raises(PackageError) as exc:
        import_trail_zip(content, data, replace=replace)
    text = " | ".join(exc.value.problems)
    for needle in needles:
        assert needle in text, text
    assert no_trash(content) == before                         # nada ficou no disco
    return exc.value


def test_importa_pacote_valido_e_ida_e_volta(tmp_path):
    content = tmp_path / "content"
    result = import_trail_zip(content, build(trail_files(tmp_path)))
    assert result["slug"] == "novo" and result["replaced"] is False and isinstance(result["warnings"], list)
    assert (content / "novo" / "block-1" / "read.md").is_file() and no_trash(content) == ["novo"]
    assert validate(content / "novo")[1] == []


def test_pack_e_import_da_trilha_real(tmp_path):
    real = ROOT / "content"
    out = tmp_path / "t.zip"
    warnings = pack_trail(real, "aprendizagem-de-maquina", out)
    assert isinstance(warnings, list) and out.is_file()
    names = zipfile.ZipFile(out).namelist()
    assert names == sorted(names) and names[0].startswith("aprendizagem-de-maquina/")
    result = import_trail_zip(tmp_path / "novo-content", out.read_bytes())
    assert result["slug"] == "aprendizagem-de-maquina" and validate(tmp_path / "novo-content" / "aprendizagem-de-maquina")[1] == []


def test_pack_deterministico_e_ignora_lixo(tmp_path, content, trail_dir):
    for junk in ("desktop.ini", ".DS_Store", "_tarefas.md", "progress.json", ".env", "x.tmp"):
        (trail_dir / junk).write_text("lixo", encoding="utf-8")
    (trail_dir / "__pycache__").mkdir()
    (trail_dir / "__pycache__" / "a.pyc").write_bytes(b"x")
    one, two = tmp_path / "a.zip", tmp_path / "b.zip"
    pack_trail(content, "demo", one)
    pack_trail(content, "demo", two)
    assert one.read_bytes() == two.read_bytes()
    names = zipfile.ZipFile(one).namelist()
    assert "demo/trail.json" in names and not any(n.endswith(("desktop.ini", ".env", "progress.json", ".pyc", ".tmp")) for n in names)
    assert all(i.date_time == (2020, 1, 1, 0, 0, 0) for i in zipfile.ZipFile(one).infolist())


def test_pack_recusa_problemas_e_extensao_proibida(tmp_path, content, trail_dir):
    (trail_dir / "figures").mkdir()
    (trail_dir / "figures" / "x.svg").write_text("<svg/>", encoding="utf-8")
    with pytest.raises(PackageError, match="extensão não permitida"):
        pack_trail(content, "demo", tmp_path / "o.zip")
    (trail_dir / "figures" / "x.svg").unlink()
    (trail_dir / "block-1" / "read.md").unlink()
    with pytest.raises(PackageError) as exc:
        pack_trail(content, "demo", tmp_path / "o.zip")
    assert any("arquivo não encontrado" in p for p in exc.value.problems)
    assert not (tmp_path / "o.zip").exists()
    with pytest.raises(PackageError, match="não encontrada"):
        pack_trail(content, "nada", tmp_path / "o.zip")


def test_recusa_caminhos_perigosos(tmp_path):
    content = tmp_path / "content"
    base = trail_files(tmp_path)
    # o zipfile normaliza "\" (no Windows) e corta no NUL ao ler: esses dois nunca chegam como perigosos
    for bad in ("novo/../fora.md", "/abs.md", "C:/x.md", "novo//x.md", "novo/./x.md", "novo/a\x01b.md"):
        refuse(content, build({**base, bad: "x"}))
    refuse(content, build({**base, "solto.md": "x"}), "fora da pasta")
    refuse(content, build({**base, "novo/link.md": "alvo"}, symlinks=("novo/link.md",)), "link simbólico")


def test_recusa_extensoes_proibidas(tmp_path):
    content = tmp_path / "content"
    base = trail_files(tmp_path)
    for name in ("novo/figures/x.svg", "novo/p.html", "novo/a.js", "novo/run.exe", "novo/semext", "novo/a.sh", "novo/x.htm"):
        refuse(content, build({**base, name: "x"}), "extensão não permitida")


def test_recusa_pasta_de_topo_errada_ou_multipla(tmp_path):
    content = tmp_path / "content"
    base = trail_files(tmp_path)
    refuse(content, build({**base, "outra/x.md": "x"}), "única pasta de topo")
    refuse(content, build({k.replace("novo/", "Novo_Ruim/"): v for k, v in base.items()}), "inválido para slug")
    refuse(content, build({"leia.md": "x"}), "fora da pasta")
    refuse(content, b"isto nao e um zip", "não é um zip")
    refuse(content, build({}), "vazio")


def test_recusa_zip_bomb_por_razao_e_por_tamanho(tmp_path, monkeypatch):
    content = tmp_path / "content"
    base = trail_files(tmp_path)
    refuse(content, build({**base, "novo/grande.txt": b"0" * 5_000_000}), "razão de compressão")
    monkeypatch.setattr(packages, "MAX_UNCOMPRESSED", 1000)
    refuse(content, build(base), "descompactado grande demais")
    monkeypatch.setattr(packages, "MAX_UNCOMPRESSED", 300 * 1024 * 1024)
    monkeypatch.setattr(packages, "MAX_FILES", 3)
    refuse(content, build(base), "arquivos demais")
    monkeypatch.setattr(packages, "MAX_FILES", 5000)
    monkeypatch.setattr(packages, "MAX_COMPRESSED", 10)
    refuse(content, build(base), "100 MB")


def test_tamanho_declarado_falso_e_pego_na_extracao(tmp_path):
    """O cabeçalho do zip mente sobre o tamanho: o que importa são os bytes realmente lidos."""
    content = tmp_path / "content"
    data = bytearray(build({**trail_files(tmp_path), "novo/mentira.txt": "x" * 5000}))
    # reduz o tamanho descompactado declarado no cabeçalho local e no diretório central
    marker = (5000).to_bytes(4, "little")
    declared = (10).to_bytes(4, "little")
    assert marker in data
    patched = bytes(data).replace(marker, declared)
    with pytest.raises(PackageError):
        import_trail_zip(content, patched)
    assert no_trash(content) == []


def test_recusa_conteudo_ativo(tmp_path):
    content = tmp_path / "content"
    base = trail_files(tmp_path)
    for payload in ("<script>alert(1)</script>", "<IFRAME src=x>", "<object data=x>", "<embed src=x>",
                    "[x](javascript:alert(1))", "data:text/html;base64,AAA", '<img src=x onerror=alert(1)>',
                    "<body onload = 'x'>"):
        refuse(content, build({**base, "novo/block-1/read.md": "# t\n" + payload}), "conteúdo perigoso")
    refuse(content, build({**base, "novo/transcripts/x.json": '{"u": "javascript:alert(1)"}'}), "conteúdo perigoso")
    refuse(content, build({**base, "novo/block-1/read.md": b"\xff\xfe\x00"}), "UTF-8")


def test_texto_comum_com_on_nao_e_confundido(tmp_path):
    content = tmp_path / "content"
    files = trail_files(tmp_path)
    files["novo/block-1/read.md"] = ("# Olá\n" + "palavra " * 360 + "\nO ciclo one = 1, confirm = 2, region = 3.").encode()
    assert import_trail_zip(content, build(files))["slug"] == "novo"


def test_recusa_manifesto_e_capa_invalidos(tmp_path):
    content = tmp_path / "content"
    base = trail_files(tmp_path)
    manifest = json.loads(base["novo/trail.json"])
    refuse(content, build({**base, "novo/trail.json": json.dumps({**manifest, "id": "outro"})}), "difere do nome da pasta")
    refuse(content, build({k: v for k, v in base.items() if k != "novo/trail.json"}), "trail.json")
    refuse(content, build({**base, "novo/trail.json": json.dumps({**manifest, "cover": "nao-existe.png"})}), "capa")
    refuse(content, build({**base, "novo/capa.gif": b"GIF89a", "novo/trail.json": json.dumps({**manifest, "cover": "capa.gif"})}),
           "png, jpg ou webp")
    refuse(content, build({**base, "novo/capa.png": os.urandom(1_000_001), "novo/trail.json": json.dumps({**manifest, "cover": "capa.png"})}),
           "1 MB")
    refuse(content, build({**base, "novo/trail.json": json.dumps({**manifest, "cover": "../fora.png"})}), "capa")
    ok = {**base, "novo/capa.png": b"png", "novo/trail.json": json.dumps({**manifest, "cover": "capa.png"})}
    assert import_trail_zip(content, build(ok))["slug"] == "novo"


def test_recusa_validacao_com_problemas(tmp_path):
    content = tmp_path / "content"
    files = trail_files(tmp_path)
    del files["novo/block-1/read.md"]
    error = refuse(content, build(files), "validação")
    assert any("arquivo não encontrado" in p for p in error.problems)


def test_slug_duplicado_exige_replace(tmp_path):
    content = tmp_path / "content"
    data = build(trail_files(tmp_path))
    import_trail_zip(content, data)
    (content / "novo" / "marca.txt").write_text("antiga", encoding="utf-8")
    refuse(content, data, "já existe")
    assert (content / "novo" / "marca.txt").is_file()
    result = import_trail_zip(content, data, replace=True)
    assert result["replaced"] is True and not (content / "novo" / "marca.txt").exists()
    assert no_trash(content) == ["novo"]


def test_replace_atomico_falha_no_meio_restaura_a_antiga(tmp_path, monkeypatch):
    content = tmp_path / "content"
    data = build(trail_files(tmp_path))
    import_trail_zip(content, data)
    (content / "novo" / "marca.txt").write_text("antiga", encoding="utf-8")

    real_rename = Path.rename

    def falha_ao_mover_a_nova(self, target):
        if Path(target).name == "novo" and self.name == "novo" and ".import-" in str(self):
            raise OSError("disco falhou")
        return real_rename(self, target)

    monkeypatch.setattr(Path, "rename", falha_ao_mover_a_nova)
    with pytest.raises(OSError):
        import_trail_zip(content, data, replace=True)
    monkeypatch.undo()
    assert (content / "novo" / "marca.txt").read_text(encoding="utf-8") == "antiga"      # a antiga voltou
    assert no_trash(content) == ["novo"]


def test_replace_com_pacote_invalido_nao_toca_na_trilha_atual(tmp_path):
    content = tmp_path / "content"
    import_trail_zip(content, build(trail_files(tmp_path)))
    (content / "novo" / "marca.txt").write_text("antiga", encoding="utf-8")
    bad = trail_files(tmp_path)
    bad["novo/block-1/read.md"] = b"<script>x</script>"
    refuse(content, build(bad), "conteúdo perigoso", replace=True)
    assert (content / "novo" / "marca.txt").is_file()


def test_pasta_temporaria_e_limpa_em_qualquer_erro(tmp_path, monkeypatch):
    content = tmp_path / "content"
    monkeypatch.setattr(packages.validator, "inspect", lambda folder: (_ for _ in ()).throw(RuntimeError("quebrou")))
    with pytest.raises(RuntimeError):
        import_trail_zip(content, build(trail_files(tmp_path)))
    assert no_trash(content) == []


def test_importado_aparece_no_indice(tmp_path, db):
    from k_study.indexer import sync
    content = tmp_path / "content"
    import_trail_zip(content, build(trail_files(tmp_path)))
    assert sync(content, db)["indexed"] == ["novo"]


# ---- specs ----

def specs_tree(root):
    (root / "specs" / "sub").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "CLAUDE.md").write_text("claude", encoding="utf-8")
    (root / "docs" / "modelo-de-dados.md").write_text("modelo", encoding="utf-8")
    (root / "docs" / "arquitetura.md").write_text("fora", encoding="utf-8")
    (root / "specs" / "01.md").write_text("um", encoding="utf-8")
    (root / "specs" / "sub" / "02.md").write_text("dois", encoding="utf-8")
    (root / ".env").write_text("K_STUDY_SECRET=x", encoding="utf-8")
    (root / "README.md").write_text("fora", encoding="utf-8")


def test_specs_zip_lista_exatamente_os_arquivos(tmp_path):
    specs_tree(tmp_path)
    archive = zipfile.ZipFile(io.BytesIO(build_specs_zip(tmp_path)))
    assert archive.namelist() == ["CLAUDE.md", "docs/modelo-de-dados.md", "specs/01.md", "specs/sub/02.md"]
    assert archive.read("specs/sub/02.md") == b"dois"


def test_specs_zip_do_projeto_real():
    names = zipfile.ZipFile(io.BytesIO(build_specs_zip(ROOT))).namelist()
    assert "CLAUDE.md" in names and "docs/modelo-de-dados.md" in names and any(n.startswith("specs/01") for n in names)
    assert not any(n.startswith((".env", "data/", "content/", "src/")) for n in names)


def test_specs_zip_erro_claro_se_faltar(tmp_path):
    with pytest.raises(PackageError, match="faltam arquivos"):
        build_specs_zip(tmp_path)


def test_specs_zip_nao_segue_symlink(tmp_path):
    specs_tree(tmp_path)
    outside = tmp_path.parent / "segredo-fora.md"
    outside.write_text("segredo", encoding="utf-8")
    try:
        (tmp_path / "specs" / "link.md").symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("sem permissão para criar links simbólicos")
    names = zipfile.ZipFile(io.BytesIO(build_specs_zip(tmp_path))).namelist()
    assert "specs/link.md" not in names
