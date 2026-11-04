"""
Projetos recentes do menu de pastas.

Guarda as ultimas pastas analisadas pelo menu, para a pessoa nao ter que
navegar de novo ate o mesmo projeto. A lista fica fora do projeto e do git:
em %APPDATA%\analisador no Windows, em ~/.config/analisador nos demais
sistemas, ou na pasta indicada pela variavel ANALISADOR_CONFIG.

Falhar aqui nunca impede a analise: arquivo ausente ou com defeito vale
lista vazia, e a falha de gravacao vira uma frase para a pessoa ouvir.
"""
import json
import os
import sys
from pathlib import Path

LIMITE = 5
VARIAVEL_CONFIG = "ANALISADOR_CONFIG"


def pasta_de_configuracao() -> Path:
    explicita = os.environ.get(VARIAVEL_CONFIG)
    if explicita:
        return Path(explicita)
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "analisador"


def arquivo_recentes() -> Path:
    return pasta_de_configuracao() / "recentes.json"


def carregar() -> list:
    """Pastas recentes que ainda existem, da mais nova para a mais antiga."""
    try:
        brutos = json.loads(arquivo_recentes().read_text(encoding="utf-8"))["recentes"]
    except (OSError, ValueError, KeyError, TypeError):
        return []
    if not isinstance(brutos, list):
        return []
    caminhos = []
    for bruto in brutos:
        if isinstance(bruto, str) and Path(bruto).exists():
            caminhos.append(Path(bruto))
    return caminhos[:LIMITE]


def registrar(caminho):
    """Poe a pasta no topo da lista. Devolve a mensagem de erro, ou None."""
    novo = Path(caminho).resolve()
    chave = os.path.normcase(str(novo))
    anteriores = [c for c in carregar() if os.path.normcase(str(c)) != chave]
    lista = [novo] + anteriores
    try:
        arquivo = arquivo_recentes()
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(
            json.dumps({"recentes": [str(c) for c in lista[:LIMITE]]},
                       ensure_ascii=False, indent=2),
            encoding="utf-8")
    except OSError as erro:
        return f"Nao consegui guardar a lista de projetos recentes: {erro}."
    return None
