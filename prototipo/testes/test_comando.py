"""
Como o comando e chamado: sem caminho vale a pasta atual do terminal, o
caminho errado e dito em palavras, e os arquivos do Windows (analisar.cmd e
instalar_comando.ps1) ficam em ASCII, com quebra de linha CRLF.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import analisador.__main__ as cli

PROTOTIPO = Path(__file__).parents[1]


def _ascii_com_crlf(conteudo: bytes):
    assert all(byte < 128 for byte in conteudo), \
        "o cmd e o PowerShell 5.1 estragam acentos de arquivo sem BOM"
    assert b"\r\n" in conteudo and b"\n" not in conteudo.replace(b"\r\n", b"")


@pytest.fixture
def casa(tmp_path, monkeypatch):
    """Pasta pessoal falsa, com um .py: o teste nunca varre a pasta real."""
    pasta = tmp_path / "casa"
    pasta.mkdir()
    (pasta / "solto.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(pasta))         # Linux e macOS
    monkeypatch.setenv("USERPROFILE", str(pasta))  # Windows
    return pasta


class FaladorFalso:
    def __init__(self):
        self.falado = []

    def verificar(self):
        pass

    def falar(self, texto):
        self.falado.append(texto)


# ---- sem caminho: a pasta atual --------------------------------------------

def test_sem_caminho_analisa_a_pasta_atual(projeto_exemplo, monkeypatch, capsys):
    monkeypatch.chdir(projeto_exemplo)
    assert cli.main([]) == 0
    saida = capsys.readouterr().out
    assert saida.startswith("Analise de projeto exemplo.")
    assert "3 arquivos analisados" in saida


def test_sem_caminho_o_json_tambem_vale_para_a_pasta_atual(projeto_exemplo, monkeypatch, capsys):
    monkeypatch.chdir(projeto_exemplo)
    assert cli.main(["--json"]) == 0
    assert json.loads(capsys.readouterr().out)["resumo_projeto"]["total_arquivos"] == 3


def test_na_pasta_pessoal_sem_caminho_nada_e_analisado(casa, monkeypatch, capsys):
    monkeypatch.chdir(casa)
    assert cli.main([]) == 1
    captura = capsys.readouterr()
    assert captura.out == ""
    assert "Voce esta na sua pasta pessoal" in captura.err
    assert "comando cd" in captura.err and "analisar --menu" in captura.err


def test_pasta_pessoal_informada_de_proposito_e_analisada(casa, monkeypatch, capsys):
    monkeypatch.chdir(casa)
    assert cli.main(["."]) == 0
    assert "1 arquivo analisado" in capsys.readouterr().out


def test_na_raiz_do_disco_sem_caminho_nada_e_analisado(casa, monkeypatch, capsys):
    monkeypatch.chdir(casa.anchor)
    assert cli.main([]) == 1
    assert "Voce esta na raiz do disco" in capsys.readouterr().err


def test_menu_continua_valendo_na_pasta_pessoal(casa, monkeypatch, capsys):
    monkeypatch.chdir(casa)
    monkeypatch.setattr("builtins.input", lambda pergunta="": "s")
    assert cli.main(["--menu"]) == 0
    assert "Erro" not in capsys.readouterr().err


def test_aviso_de_pasta_errada_tambem_e_falado(casa, monkeypatch):
    falador = FaladorFalso()
    monkeypatch.setattr(cli, "criar_falador", lambda *args, **kwargs: falador)
    monkeypatch.chdir(casa)
    assert cli.main(["--falar"]) == 1
    assert len(falador.falado) == 1
    assert "pasta pessoal" in falador.falado[0]


# ---- caminho informado ------------------------------------------------------

def test_caminho_que_nao_existe_e_dito_e_nada_e_analisado(tmp_path, capsys):
    assert cli.main([str(tmp_path / "projeto_que_nao_existe")]) == 1
    captura = capsys.readouterr()
    assert captura.out == ""
    assert "Nao encontrei" in captura.err and "projeto_que_nao_existe" in captura.err


def test_arquivo_que_nao_e_python_e_dito(tmp_path, capsys):
    leia = tmp_path / "leia.txt"
    leia.write_text("x", encoding="utf-8")
    assert cli.main([str(leia)]) == 1
    assert "leia.txt nao e um arquivo Python" in capsys.readouterr().err


def test_pasta_sem_python_nao_soa_como_codigo_sem_problema(tmp_path, capsys):
    (tmp_path / "leia.txt").write_text("x", encoding="utf-8")
    assert cli.main([str(tmp_path)]) == 0
    saida = capsys.readouterr().out
    assert "Nenhum arquivo Python foi encontrado" in saida
    assert "Nenhum ponto critico" not in saida


def test_pasta_sem_python_nao_chama_o_modelo(tmp_path, monkeypatch, capsys):
    def nao_chamar(*args, **kwargs):
        raise AssertionError("sem arquivo Python, o modelo nao deve ser chamado")
    monkeypatch.setattr(cli, "criar_explicador", nao_chamar)
    assert cli.main([str(tmp_path), "--explicar"]) == 0
    assert "Nenhum arquivo Python foi encontrado" in capsys.readouterr().out


# ---- arquivos do Windows ----------------------------------------------------

def test_atalho_cmd_e_ascii_e_tem_quebra_de_linha_do_windows():
    conteudo = (PROTOTIPO / "analisar.cmd").read_bytes()
    _ascii_com_crlf(conteudo)
    assert b"-m analisador %*" in conteudo


def test_atalho_cmd_nao_poe_a_pasta_do_projeto_na_frente_das_bibliotecas():
    conteudo = (PROTOTIPO / "analisar.cmd").read_bytes()
    assert b'set "PYTHONSAFEPATH=1"' in conteudo
    assert conteudo.index(b"PYTHONSAFEPATH") < conteudo.index(b"-m analisador")


@pytest.mark.skipif(sys.version_info < (3, 11),
                    reason="PYTHONSAFEPATH existe a partir do Python 3.11")
def test_arquivo_do_projeto_com_nome_de_biblioteca_nao_e_executado(tmp_path):
    """Com python -m, a pasta atual vai para a frente das bibliotecas: um
    json.py do projeto rodaria no lugar do json padrao. O analisar.cmd liga
    o PYTHONSAFEPATH para isso nao acontecer quando o comando roda no projeto."""
    projeto = tmp_path / "projeto"
    projeto.mkdir()
    marca = tmp_path / "json_do_projeto_rodou"
    (projeto / "json.py").write_text(f"open({str(marca)!r}, 'w').close()\n",
                                     encoding="utf-8")
    ambiente = dict(os.environ, PYTHONPATH=str(PROTOTIPO))
    ambiente.pop("PYTHONSAFEPATH", None)

    subprocess.run([sys.executable, "-m", "analisador"], cwd=projeto,
                   env=ambiente, capture_output=True, timeout=120)
    assert marca.exists(), "sem a protecao, o json.py do projeto roda"

    marca.unlink()
    ambiente["PYTHONSAFEPATH"] = "1"
    subprocess.run([sys.executable, "-m", "analisador"], cwd=projeto,
                   env=ambiente, capture_output=True, timeout=120)
    assert not marca.exists()


def test_instalador_do_comando_e_ascii_e_tem_quebra_de_linha_do_windows():
    _ascii_com_crlf((PROTOTIPO / "instalar_comando.ps1").read_bytes())


def test_instalador_mexe_so_no_path_do_usuario_e_preserva_as_variaveis():
    """O script so roda no Windows; aqui se confere o que ele promete."""
    texto = (PROTOTIPO / "instalar_comando.ps1").read_text(encoding="ascii")
    codigo = "\n".join(linha for linha in texto.splitlines()
                       if not linha.lstrip().startswith("#"))
    assert "CurrentUser" in codigo
    assert "LocalMachine" not in codigo and '"Machine"' not in codigo
    assert "DoNotExpandEnvironmentNames" in codigo
    assert "$Remover" in codigo
