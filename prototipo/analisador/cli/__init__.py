"""
Fase 4 (secao 13 do documento). Interface de terminal.

- navegador.py: menu de pastas. Escolhe o que analisar navegando um nivel
  por vez, sem digitar caminho (implementado). Aberto por
  "python -m analisador" sem caminho.
- recentes.py: lembra os ultimos projetos analisados pelo menu.
- texto.py: concordancia e nomes falaveis, compartilhados com o relatorio.

Ainda nao implementado: a navegacao pelos resultados (proxima regiao,
repetir, explicacao sob demanda), caso de uso da secao 12 do documento.
"""
from analisador.cli.navegador import Escolha, escolher_pasta  # noqa: F401
