"""
Menu de pastas (Fase 4): navegacao por um nivel, escolha de escopo, projetos
recentes e a integracao com a CLI. Sem terminal: entrada e saida sao falsas.
"""
import json
import re
from pathlib import Path

import pytest

import analisador.__main__ as cli
from analisador.analise import analisar
from analisador.cli import navegador, recentes
from analisador.cli.navegador import contar_python, escolher_pasta, listar_nivel
from analisador.parser.varredura import PASTAS_IGNORADAS


class Roteiro:
    """Entrada falsa: responde na ordem e, acabadas as respostas, fecha a entrada."""

    def __init__(self, *respostas):
        self.respostas = list(respostas)

    def __call__(self, pergunta=""):
        if not self.respostas:
            raise EOFError
        return self.respostas.pop(0)


def rodar(inicio, *respostas, **opcoes):
    """Roda o menu com as respostas dadas. Devolve (escolha, texto falado)."""
    falado = []
    escolha = escolher_pasta(inicio=inicio, entrada=Roteiro(*respostas),
                             saida=falado.append, **opcoes)
    return escolha, "\n".join(falado)


def _py(raiz, *partes):
    arquivo = raiz.joinpath(*partes)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text("x = 1\n", encoding="utf-8")


@pytest.fixture
def arvore(tmp_path):
    """alfa (2 .py), beta (so em sub), delta (1 solto e 1 em sub); gama sem
    codigo, .venv e node_modules ignoradas; mais um .py solto na raiz."""
    raiz = tmp_path / "raiz"
    _py(raiz, "alfa", "a1.py")
    _py(raiz, "alfa", "a2.py")
    _py(raiz, "beta", "sub", "b1.py")
    _py(raiz, "delta", "d1.py")
    _py(raiz, "delta", "sub", "d2.py")
    (raiz / "gama").mkdir()
    (raiz / "gama" / "leia.txt").write_text("x", encoding="utf-8")
    _py(raiz, ".venv", "v.py")
    _py(raiz, "node_modules", "n.py")
    _py(raiz, "solto.py")
    return raiz


# ---- listagem de um nivel ------------------------------------------------

def test_lista_so_o_primeiro_nivel_e_so_pastas_com_codigo(arvore):
    nivel = listar_nivel(arvore)
    assert [s.nome for s in nivel.subpastas] == ["alfa", "beta", "delta"]
    assert {s.nome: s.arquivos_py for s in nivel.subpastas} == {"alfa": 2, "beta": 1, "delta": 2}
    assert nivel.soltos == 1
    assert nivel.ocultas == 3  # gama (sem codigo), .venv e node_modules


def test_contagem_usa_as_mesmas_regras_da_analise(arvore):
    total, completa = contar_python(arvore)
    assert completa
    assert total == len(analisar(arvore).mapa.arquivos)


def test_contagem_para_no_limite_e_diz_que_esta_incompleta(tmp_path):
    fundo = tmp_path
    for i in range(5):
        fundo = fundo / f"n{i}"
    _py(fundo, "x.py")
    total, completa = contar_python(tmp_path, limite=2)
    assert completa is False
    assert total == 0


# ---- o que a pessoa ouve -------------------------------------------------

def test_tela_diz_onde_esta_quantas_pastas_ha_e_o_que_foi_ocultado(arvore):
    escolha, falado = rodar(arvore, "s")
    assert escolha is None
    assert "Voce esta na pasta raiz" in falado
    assert "Ha 3 pastas com codigo Python e 1 arquivo Python solto nesta pasta." in falado
    assert "1, alfa, 2 arquivos Python." in falado
    assert "3, delta, 2 arquivos Python." in falado
    assert "Ocultei 3 pastas sem codigo Python ou de sistema." in falado
    assert "Encerrado. Nada foi analisado." in falado


def test_pasta_gigante_diz_pelo_menos_em_vez_de_travar(arvore):
    nivel = listar_nivel(arvore, limite=1)  # so uma pasta visitada por subpasta
    contagens = {s.nome: (s.arquivos_py, s.completa) for s in nivel.subpastas}
    assert contagens == {"alfa": (2, True), "beta": (0, False), "delta": (1, False)}
    assert nivel.ocultas == 3  # gama cabe no limite e e vazia de verdade


def test_contagem_incompleta_e_dita_sem_inventar_numero():
    pasta = navegador.Subpasta("x", Path("x"), 0, completa=False)
    assert navegador._contagem(pasta) == "muitos arquivos, nao consegui contar os de Python"
    pasta.arquivos_py = 3
    assert navegador._contagem(pasta) == "pelo menos 3 arquivos Python"


def test_texto_e_curto_e_sem_simbolos_decorativos(arvore):
    _, falado = rodar(arvore, "?", "3", "a", "2")
    for simbolo in ("|", "+--", "===", "***", "```", "#"):
        assert simbolo not in falado
    for linha in falado.splitlines():
        for frase in re.split(r"[.!?]\s", linha):
            assert len(frase.split()) <= 20, f"frase longa demais para ouvir: {frase!r}"


def test_ajuda_e_enter_repete_a_tela(arvore):
    _, falado = rodar(arvore, "?", "", "s")
    assert "Ajuda." in falado
    assert falado.count("Voce esta na pasta raiz") == 2  # tela inicial + Enter


# ---- navegacao -----------------------------------------------------------

def test_entrar_numa_pasta_e_analisar(arvore):
    escolha, falado = rodar(arvore, "1", "a", "s")
    assert escolha.caminho == arvore / "alfa"
    assert escolha.ignorar is None and escolha.abrangencia is None
    assert "Voce esta na pasta alfa, dentro de raiz." in falado
    assert "Vou analisar a pasta alfa: 2 arquivos Python." in falado


def test_so_os_arquivos_soltos_ignora_as_subpastas(arvore):
    escolha, falado = rodar(arvore, "3", "a", "2")
    assert "Digite 1 para analisar com as subpastas: 2 arquivos Python." in falado
    assert "Digite 2 para analisar so os arquivos desta pasta: 1 arquivo Python." in falado
    assert escolha.abrangencia == navegador.ABRANGENCIA_SOLTOS
    assert "sub" in escolha.ignorar and PASTAS_IGNORADAS <= escolha.ignorar
    resultado = analisar(escolha.caminho, ignorar=escolha.ignorar)
    assert [a.relativo for a in resultado.mapa.arquivos] == ["d1.py"]


def test_pasta_inteira_inclui_as_subpastas(arvore):
    escolha, _ = rodar(arvore, "3", "a", "1")
    assert escolha.ignorar is None
    assert len(analisar(escolha.caminho).mapa.arquivos) == 2


def test_pasta_so_com_codigo_em_subpastas_avisa(arvore):
    escolha, falado = rodar(arvore, "2", "a", "s")
    assert "todos em subpastas" in falado
    assert escolha.caminho == arvore / "beta"


def test_enter_na_confirmacao_volta_sem_analisar(arvore):
    escolha, falado = rodar(arvore, "1", "a", "", "s")
    assert escolha is None
    assert falado.count("Voce esta na pasta alfa") == 2


def test_voltar_uma_pasta(arvore):
    escolha, falado = rodar(arvore / "alfa", "v", "s")
    assert escolha is None
    assert "Ha 3 pastas com codigo Python" in falado


def test_numero_fora_da_lista_diz_o_limite(arvore):
    _, falado = rodar(arvore, "9", "s")
    assert "Nao existe a opcao 9. Escolha de 1 a 3." in falado


def test_digito_que_nao_e_numero_nao_derruba_o_menu(arvore):
    # "²".isdigit() e verdadeiro, mas int("²") levanta ValueError
    _, falado = rodar(arvore, "²", "s")
    assert "Encerrado." in falado


def test_pasta_sem_python_nao_e_analisada(arvore):
    escolha, falado = rodar(arvore, str(arvore / "gama"), "a", "s")
    assert escolha is None
    assert "Nao ha arquivos Python na pasta gama nem nas suas subpastas." in falado


# ---- atalhos: filtro, caminho colado, paginacao ---------------------------

def test_filtro_ignora_acento_caixa_e_sublinhado(tmp_path):
    _py(tmp_path, "Relatórios_Mensais", "r.py")
    _py(tmp_path, "outra", "o.py")
    escolha, falado = rodar(tmp_path, "RELATORIOS mensais", "1", "a", "s")
    assert "Filtro: RELATORIOS mensais. 1 pasta encontrada." in falado
    assert escolha.caminho == tmp_path / "Relatórios_Mensais"


def test_filtro_sem_resultado_mantem_a_lista(arvore):
    escolha, falado = rodar(arvore, "zzz", "1", "a", "s")
    assert "Nenhuma pasta tem zzz no nome. A lista continua como estava." in falado
    assert escolha.caminho == arvore / "alfa"


def test_limpar_filtro_volta_a_lista_inteira(arvore):
    _, falado = rodar(arvore, "alf", "l", "s")
    assert "Filtro: alf. 1 pasta encontrada." in falado
    assert falado.rstrip().splitlines()[-2].startswith("Digite o numero")
    assert falado.count("Ha 3 pastas com codigo Python") == 2


def test_paginacao_tem_numeros_absolutos_e_recomeca_no_fim(tmp_path):
    for i in range(1, 11):
        _py(tmp_path, f"p{i:02d}", "x.py")
    _, falado = rodar(tmp_path, "m", "m", "s")
    assert "Mostrando de 1 a 7 de 10." in falado
    assert "7, p07, 1 arquivo Python." in falado
    assert "Mostrando de 8 a 10 de 10." in falado
    assert "8, p08, 1 arquivo Python." in falado
    assert "Fim da lista, recomecando do inicio." in falado


def test_numero_da_segunda_tela_vale_sem_pedir_mais(tmp_path):
    for i in range(1, 11):
        _py(tmp_path, f"p{i:02d}", "x.py")
    escolha, _ = rodar(tmp_path, "8", "a", "s")
    assert escolha.caminho == tmp_path / "p08"


def test_caminho_colado_do_explorador_leva_direto_para_a_pasta(arvore):
    colado = f'"{arvore / "alfa"}"'  # "Copiar como caminho" do Explorador poe aspas
    escolha, falado = rodar(arvore, colado, "a", "s")
    assert escolha.caminho == (arvore / "alfa").resolve()
    assert "Voce esta na pasta alfa" in falado


def test_caminho_colado_que_nao_existe_e_dito(arvore):
    _, falado = rodar(arvore, str(arvore / "nao_existe"), "s")
    assert "Nao encontrei esse caminho." in falado


def test_caminho_colado_de_arquivo_python(arvore):
    escolha, falado = rodar(arvore, str(arvore / "alfa" / "a1.py"), "s")
    assert "Vou analisar o arquivo a1.py." in falado
    assert escolha.caminho == (arvore / "alfa" / "a1.py").resolve()
    assert escolha.ignorar is None


# ---- falhas ---------------------------------------------------------------

def test_pasta_que_nao_abre_e_dita_e_a_pessoa_continua_onde_estava(arvore, monkeypatch):
    original = navegador.listar_nivel

    def falha(pasta, *args, **kwargs):
        if Path(pasta).name == "alfa":
            raise PermissionError(13, "Permission denied")
        return original(pasta, *args, **kwargs)

    monkeypatch.setattr(navegador, "listar_nivel", falha)
    _, falado = rodar(arvore, "1", "s")
    assert "Nao consegui abrir a pasta alfa: Permission denied. Continuo em raiz." in falado


def test_fim_da_entrada_encerra_sem_travar(arvore):
    escolha, falado = rodar(arvore)
    assert escolha is None
    assert "Encerrado. Nada foi analisado." in falado


def test_ctrl_c_encerra(arvore):
    def interrompe(pergunta=""):
        raise KeyboardInterrupt

    falado = []
    assert escolher_pasta(inicio=arvore, entrada=interrompe, saida=falado.append) is None
    assert "Encerrado." in falado[-1]


def test_aviso_do_modelo_so_aparece_com_explicacao(arvore):
    _, sem = rodar(arvore, "1", "a", "s")
    _, com = rodar(arvore, "1", "a", "s", com_explicacao=True)
    assert "segundos a minutos" not in sem
    assert "segundos a minutos" in com


def test_aviso_de_abrangencia_e_dito_uma_vez_por_sessao(arvore):
    _, falado = rodar(arvore, "1", "a", "", "a", "")
    assert falado.count("Atencao: a analise considera so o que esta dentro da escolha.") == 1


# ---- projetos recentes ----------------------------------------------------

def test_ultimo_projeto_e_oferecido_na_partida(arvore, monkeypatch):
    monkeypatch.chdir(arvore)
    primeira, _ = rodar(None, "1", "a", "s")
    assert primeira.caminho.resolve() == (arvore / "alfa").resolve()

    escolha, falado = rodar(None, "1", "s")
    assert "Ultimo projeto analisado: alfa, dentro de raiz." in falado
    assert escolha.caminho.resolve() == (arvore / "alfa").resolve()


def test_recusar_o_ultimo_projeto_abre_a_navegacao(arvore, monkeypatch):
    monkeypatch.chdir(arvore)
    rodar(None, "1", "a", "s")
    escolha, falado = rodar(None, "2", "s")
    assert escolha is None
    assert "Ha 3 pastas com codigo Python" in falado


def test_comando_r_lista_os_recentes_e_escolhe_um(arvore):
    recentes.registrar(arvore / "delta")
    escolha, falado = rodar(arvore, "r", "1", "2")
    assert "Projetos recentes." in falado
    assert "1, delta, dentro de raiz." in falado
    assert escolha.caminho == (arvore / "delta").resolve()
    assert escolha.abrangencia == navegador.ABRANGENCIA_SOLTOS


def test_r_sem_recentes_diz_que_nao_ha(arvore):
    _, falado = rodar(arvore, "r", "s")
    assert "Ainda nao ha projetos recentes." in falado


def test_recentes_sem_repeticao_limitados_e_mais_novo_primeiro(tmp_path):
    pastas = []
    for i in range(7):
        pasta = tmp_path / f"proj{i}"
        pasta.mkdir()
        pastas.append(pasta)
        assert recentes.registrar(pasta) is None
    recentes.registrar(pastas[4])  # repetida: sobe para o topo, sem duplicar
    lista = recentes.carregar()
    assert [p.name for p in lista] == ["proj4", "proj6", "proj5", "proj3", "proj2"]


def test_recentes_esquece_pasta_que_deixou_de_existir(tmp_path):
    pasta = tmp_path / "some"
    pasta.mkdir()
    recentes.registrar(pasta)
    pasta.rmdir()
    assert recentes.carregar() == []


def test_arquivo_de_recentes_com_defeito_vale_lista_vazia():
    arquivo = recentes.arquivo_recentes()
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text("isto nao e json", encoding="utf-8")
    assert recentes.carregar() == []


def test_falha_ao_guardar_recentes_e_dita_e_a_escolha_segue(arvore, tmp_path, monkeypatch):
    arquivo_comum = tmp_path / "ocupado"
    arquivo_comum.write_text("x", encoding="utf-8")
    monkeypatch.setenv("ANALISADOR_CONFIG", str(arquivo_comum / "config"))
    escolha, falado = rodar(arvore, "1", "a", "s")
    assert escolha.caminho == arvore / "alfa"
    assert "Nao consegui guardar a lista de projetos recentes" in falado


# ---- integracao com a CLI -------------------------------------------------

def test_cli_com_menu_abre_o_menu_e_analisa(arvore, monkeypatch, capsys):
    monkeypatch.chdir(arvore)
    monkeypatch.setattr("builtins.input", Roteiro("1", "a", "s"))
    assert cli.main(["--menu"]) == 0
    saida = capsys.readouterr().out
    assert "Voce esta na pasta raiz" in saida
    assert "Analise de alfa." in saida
    assert "2 arquivos analisados" in saida


def test_cli_diz_o_escopo_quando_so_os_arquivos_soltos(arvore, monkeypatch, capsys):
    monkeypatch.chdir(arvore)
    monkeypatch.setattr("builtins.input", Roteiro("3", "a", "2"))
    assert cli.main(["--menu"]) == 0
    saida = capsys.readouterr().out
    assert "Escopo: somente os arquivos desta pasta, sem as subpastas." in saida
    assert "1 arquivo analisado" in saida


def test_cli_sair_do_menu_nao_analisa_nada(arvore, monkeypatch, capsys):
    monkeypatch.chdir(arvore)
    monkeypatch.setattr("builtins.input", Roteiro("s"))
    assert cli.main(["--menu"]) == 0
    assert "Analise de" not in capsys.readouterr().out


def test_cli_menu_com_json_e_recusado(capsys):
    with pytest.raises(SystemExit) as saida:
        cli.main(["--menu", "--json"])
    assert saida.value.code == 2
    assert "--menu nao se combina com --json" in capsys.readouterr().err


def test_cli_menu_com_caminho_comeca_nele(arvore, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", Roteiro("a", "s"))
    assert cli.main(["--menu", str(arvore / "alfa")]) == 0
    saida = capsys.readouterr().out
    assert "Voce esta na pasta alfa" in saida
    assert "Analise de alfa." in saida


def test_cli_menu_com_arquivo_diz_que_o_menu_comeca_numa_pasta(arvore, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", Roteiro())  # o menu nem deve abrir
    assert cli.main(["--menu", str(arvore / "solto.py")]) == 1
    assert "O menu comeca numa pasta" in capsys.readouterr().err


def test_relatorio_fala_o_nome_da_pasta_e_nao_o_caminho(projeto_exemplo, monkeypatch, capsys):
    cli.main([str(projeto_exemplo)])
    assert capsys.readouterr().out.startswith("Analise de projeto exemplo.")
    monkeypatch.chdir(projeto_exemplo)
    cli.main(["."])
    primeira_linha = capsys.readouterr().out.splitlines()[0]
    assert primeira_linha == "Analise de projeto exemplo."


# ---- --saida: UTF-8 sem passar pelo redirecionamento do PowerShell --------

def test_saida_grava_o_mesmo_texto_que_imprime(projeto_exemplo, tmp_path, capsys):
    arquivo = tmp_path / "saida_relatorio.txt"
    assert cli.main([str(projeto_exemplo), "--saida", str(arquivo)]) == 0
    captura = capsys.readouterr()
    assert arquivo.read_text(encoding="utf-8-sig") == captura.out
    assert "Relatorio gravado em" in captura.err


def test_saida_json_e_json_valido_sem_bom(projeto_exemplo, tmp_path):
    arquivo = tmp_path / "saida_relatorio.json"
    assert cli.main([str(projeto_exemplo), "--json", "--saida", str(arquivo)]) == 0
    assert not arquivo.read_bytes().startswith(b"\xef\xbb\xbf")
    assert json.loads(arquivo.read_text(encoding="utf-8"))["resumo_projeto"]["total_arquivos"] == 3


def test_saida_preserva_acentos_em_utf8(tmp_path):
    arquivo = tmp_path / "saida_acentos.json"
    assert cli._gravar_saida(str(arquivo), "Inferência: ação", como_json=True) is None
    assert "Inferência: ação".encode("utf-8") in arquivo.read_bytes()
    texto = tmp_path / "saida_acentos.txt"
    assert cli._gravar_saida(str(texto), "Inferência", como_json=False) is None
    assert texto.read_bytes().startswith(b"\xef\xbb\xbf")


def test_saida_que_nao_pode_ser_gravada_e_dita_e_muda_o_codigo(projeto_exemplo, tmp_path, capsys):
    codigo = cli.main([str(projeto_exemplo), "--saida", str(tmp_path)])  # pasta, nao arquivo
    captura = capsys.readouterr()
    assert codigo == 4
    assert "Nao foi possivel gravar o relatorio" in captura.err
    assert "Analise de projeto exemplo." in captura.out  # o relatorio sai mesmo assim
