import json

from k_study.validate import inspect, trail_slugs, validate


def edit(path, change):
    doc = json.loads(path.read_text(encoding="utf-8"))
    change(doc)
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_trilha_valida_nao_tem_problemas(trail_dir):
    summary, problems = validate(trail_dir)
    assert problems == []
    assert summary == ["block-1: 3 itens, 1 vídeos, 1 questões"]


def test_cada_alternativa_precisa_de_explicacao(trail_dir):
    edit(trail_dir / "block-1" / "q.json", lambda d: d["questions"][0]["options"][1].update(explanation=""))
    assert any("alternativa sem explicação" in p for p in validate(trail_dir)[1])


def test_questao_single_precisa_de_exatamente_uma_correta(trail_dir):
    edit(trail_dir / "block-1" / "q.json", lambda d: d["questions"][0]["options"][1].update(correct=True))
    assert any("'single' com 2 alternativas corretas" in p for p in validate(trail_dir)[1])


def test_falta_general_explanation(trail_dir):
    edit(trail_dir / "block-1" / "q.json", lambda d: d["questions"][0].pop("generalExplanation"))
    assert any("generalExplanation" in p for p in validate(trail_dir)[1])


def test_arquivo_ausente_e_trecho_invalido(trail_dir):
    def change(doc):
        doc["sections"][0]["items"][0]["path"] = "nope.md"
        doc["sections"][0]["items"][1]["clips"] = [{"start": 9, "end": 3}]
    edit(trail_dir / "block-1" / "block.json", change)
    problems = validate(trail_dir)[1]
    assert any("arquivo não encontrado" in p for p in problems) and any("fim <= início" in p for p in problems)


def set_clip(trail_dir, start, end):
    def change(doc):
        video = next(i for s in doc["sections"] for i in s["items"] if i["type"] == "video")
        video["clips"] = [{"start": start, "end": end}]
    edit(trail_dir / "block-1" / "block.json", change)


def test_trecho_alem_do_fim_so_avisa_e_respeita_a_tolerancia(trail_dir):
    set_clip(trail_dir, 0, 35)                      # 25 s além de um vídeo de 10 s: dentro da tolerância de 30 s
    _, problems, warnings = inspect(trail_dir)
    assert problems == [] and not any("além do fim" in w for w in warnings)
    set_clip(trail_dir, 0, 200)
    _, problems, warnings = inspect(trail_dir)
    assert problems == [] and any("além do fim" in w for w in warnings)
    set_clip(trail_dir, 50, 60)
    assert any("depois do fim" in w for w in inspect(trail_dir)[2])


def test_escape_quebrado_reprova_mas_latex_so_avisa(trail_dir):
    path = trail_dir / "block-1" / "q.json"
    edit(path, lambda d: d["questions"][0]["options"][0].update(text="valor $" + chr(92) + "beta$ = 0"))
    _, problems, warnings = inspect(trail_dir)
    assert problems == [] and any("LaTeX" in w for w in warnings)
    edit(path, lambda d: d["questions"][0]["options"][0].update(text="valor " + chr(8) + "eta = 0"))
    assert any("caractere de controle" in p for p in inspect(trail_dir)[1])


def test_heuristicas_de_posicao_leitura_curta_e_explicacao_curta_so_avisam(trail_dir):
    def many(doc):
        base = doc["questions"][0]
        doc["questions"] = [dict(base, id=f"q{i:02d}") for i in range(8)]
        for q in doc["questions"]:
            q["options"][0]["text"] = "resposta bem mais longa que a outra alternativa"
    edit(trail_dir / "block-1" / "q.json", many)
    (trail_dir / "block-1" / "read.md").write_text("curta\n", encoding="utf-8")
    _, problems, warnings = inspect(trail_dir)
    assert problems == []
    assert any("a mais longa" in w for w in warnings) and any("leitura curta" in w for w in warnings)
    assert any("menos de 40 caracteres" in w for w in warnings)


def test_imagem_ausente_na_leitura(trail_dir):
    (trail_dir / "block-1" / "read.md").write_text("![x](../figures/nao.png)\n", encoding="utf-8")
    assert any("imagem não encontrada" in p for p in validate(trail_dir)[1])


def test_caminho_fora_da_trilha_e_transcricao_ausente(trail_dir):
    def change(doc):
        doc["sections"][0]["items"][0]["path"] = "../../fora.md"
        doc["sections"][0]["items"][1]["transcript"] = "../transcripts/nada.json"
    edit(trail_dir / "block-1" / "block.json", change)
    problems = validate(trail_dir)[1]
    assert any("sai da pasta" in p for p in problems) and any("transcrição não encontrada" in p for p in problems)


def test_url_de_video_invalida(trail_dir):
    edit(trail_dir / "block-1" / "block.json", lambda d: d["sections"][0]["items"][1].update(url="http://x.org"))
    assert any("URL de vídeo inválida" in p for p in validate(trail_dir)[1])


def test_manifesto_da_trilha(trail_dir):
    manifest = trail_dir / "trail.json"
    edit(manifest, lambda d: d.update(id="outro", schema="trail/v2", title=""))
    problems = validate(trail_dir)[1]
    assert any("difere do nome da pasta" in p for p in problems)
    assert any("trail/v1" in p for p in problems) and any("título" in p for p in problems)


def test_bloco_inexistente_e_id_de_bloco_diferente(trail_dir):
    edit(trail_dir / "trail.json", lambda d: d["blocks"].append({"id": "block-2", "title": "X", "file": "block-2/block.json"}))
    assert any("arquivo do bloco não encontrado" in p for p in validate(trail_dir)[1])
    edit(trail_dir / "block-1" / "block.json", lambda d: d.update(id="block-9"))
    assert any("difere do trail.json" in p for p in validate(trail_dir)[1])


def test_slug_invalido_e_json_quebrado(tmp_path, trail_dir):
    bad = tmp_path / "Pasta Ruim"
    bad.mkdir()
    (bad / "trail.json").write_text("{quebrado", encoding="utf-8")
    problems = validate(bad)[1]
    assert problems and "trail.json inválido" in problems[0]
    assert validate(tmp_path / "nada")[1] == ["trail.json não encontrado em nada/"]
    (bad / "trail.json").write_text(trail_dir.joinpath("trail.json").read_text(encoding="utf-8"), encoding="utf-8")
    assert any("slug inválido" in p for p in validate(bad)[1])


def test_json_de_questoes_quebrado_nao_derruba_o_validador(trail_dir):
    (trail_dir / "block-1" / "q.json").write_text("{quebrado", encoding="utf-8")
    assert any("arquivo de questões inválido" in p for p in validate(trail_dir)[1])


def test_lista_de_trilhas(content):
    assert trail_slugs(content) == ["demo"]
    assert trail_slugs(content / "nao-existe") == []


def test_capa_do_manifesto(trail_dir):
    def set_cover(value):
        edit(trail_dir / "trail.json", lambda d: d.update(cover=value))
        return validate(trail_dir)[1]

    (trail_dir / "capa.png").write_bytes(b"x")
    assert set_cover("capa.png") == []
    assert any("capa não encontrada" in p for p in set_cover("nao-existe.png"))
    assert any("png, jpg ou webp" in p for p in set_cover("block-1/read.md"))
    assert any("dentro da pasta" in p for p in set_cover("../fora.png"))
    (trail_dir / "grande.webp").write_bytes(b"x" * 1_000_001)
    assert any("1 MB" in p for p in set_cover("grande.webp"))
