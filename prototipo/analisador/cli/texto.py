"""
Texto para quem ouve: concordancia e nomes que a sintese de voz le bem.

Usado pelo menu de pastas e pelo cabecalho do relatorio.
"""
from pathlib import Path


def plural(quantidade: int, singular: str, plural: str) -> str:
    """Concorda numero e substantivo: "1 pasta", "3 pastas"."""
    return f"{quantidade} {singular if quantidade == 1 else plural}"


def falavel(nome: str) -> str:
    """Troca sublinhado e hifen por espaco.

    Conforme o nivel de pontuacao do leitor de tela, esses simbolos sao
    falados por extenso ("projeto sublinhado exemplo"), o que atrasa e
    confunde quem so ouve. O nome real continua intacto no sistema."""
    return " ".join(nome.replace("_", " ").replace("-", " ").split())


def nome_falavel(caminho) -> str:
    """Nome da pasta ou do arquivo, sem o caminho em volta.

    "." seria lido como "ponto", e um caminho completo viraria uma
    sequencia de barras e dois pontos."""
    try:
        caminho = Path(caminho).resolve()
    except OSError:
        caminho = Path(caminho)
    return falavel(caminho.name) or (caminho.drive or str(caminho))
