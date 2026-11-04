"""
Caminhos compartilhados pelos testes.
"""
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def projeto_exemplo():
    """Projeto de tres arquivos que se importam (secao 12 do documento)."""
    return FIXTURES / "projeto_exemplo"


@pytest.fixture
def projeto_quebrado():
    """Projeto com um arquivo de sintaxe invalida."""
    return FIXTURES / "projeto_quebrado"


@pytest.fixture
def arquivo_funcionarios():
    """Fixture original da Fase 1, em arquivo unico."""
    return FIXTURES / "exemplo_funcionarios.py"


@pytest.fixture
def ollama():
    """Servidor Ollama falso, no ar durante o teste."""
    from testes.ollama_falso import OllamaFalso

    servidor = OllamaFalso().iniciar()
    yield servidor
    servidor.parar()


@pytest.fixture(autouse=True)
def _config_isolada(tmp_path, monkeypatch):
    """A lista de projetos recentes do usuario nunca e lida nem gravada em teste."""
    monkeypatch.setenv("ANALISADOR_CONFIG", str(tmp_path / "config_analisador"))
