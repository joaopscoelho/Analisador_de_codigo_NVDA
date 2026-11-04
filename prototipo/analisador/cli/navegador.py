"""
Menu de pastas: escolhe o que analisar navegando um nivel de cada vez.

Fase 4 (secao 13 do documento). O runner antigo pedia o caminho completo
da pasta, ou seja, exigia que a pessoa soubesse e digitasse onde o projeto
esta -- justamente a navegacao entre pastas e arquivos que a literatura do
TCC aponta como barreira (latinoware20457). Este menu faz essa navegacao
por ela, com perguntas curtas.

Decisoes, para ler antes de mexer:

- Um nivel por vez, nunca a arvore inteira. Cada tela diz onde a pessoa
  esta, quantas pastas com codigo existem ali e lista no maximo POR_TELA
  delas; "m" mostra as seguintes.
- Pastas sem codigo Python, de sistema ou de ferramenta (.venv, .git,
  node_modules...) nao entram na lista, mas a tela diz quantas foram
  ocultadas: ocultar em silencio faria a pessoa achar que a pasta nao existe.
- Linhas simples, lidas por qualquer leitor de tela: so input() e print(),
  sem limpar a tela, sem cores, sem setas nem teclas especiais. O leitor de
  tela fala o que o terminal imprime, entao este modulo nao chama a DLL do
  NVDA; a fala por DLL continua sendo so do relatorio (--falar).
- Numeros absolutos na lista inteira (a segunda tela comeca em 8), para o
  numero ouvido continuar valendo.
- Enter sozinho repete a tela: quem ouve nao "olha de novo".
- Atalhos para nao navegar: parte do nome filtra a lista, o caminho completo
  copiado do Explorador leva direto para a pasta, e o ultimo projeto e
  oferecido na partida.
- O escopo e dito antes de analisar. Analisar so uma subpasta perde as
  chamadas que vem de fora dela, e a pessoa precisa saber disso.
- Entrada e saida sao injetaveis: os testes rodam sem terminal.
- Nenhuma tela tem acento, como o restante do relatorio da CLI.
"""
import os
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from analisador.cli import recentes
from analisador.cli.texto import falavel, plural
from analisador.parser.varredura import PASTAS_IGNORADAS

POR_TELA = 7
#: Pastas visitadas, no maximo, ao contar os .py dentro de uma subpasta. Em
#: pastas gigantes (a pasta pessoal, por exemplo) a contagem para aqui e a
#: tela diz "pelo menos", em vez de travar a navegacao.
LIMITE_PASTAS_NA_CONTAGEM = 2000
ABRANGENCIA_SOLTOS = "somente os arquivos desta pasta, sem as subpastas"


@dataclass
class Subpasta:
    """Subpasta com codigo Python, como aparece na lista."""

    nome: str
    caminho: Path
    arquivos_py: int
    completa: bool = True


@dataclass
class Nivel:
    """Conteudo de uma pasta que interessa ao menu."""

    pasta: Path
    subpastas: list
    ocultas: int
    soltos: int


@dataclass
class Escolha:
    """O que a pessoa decidiu analisar.

    ignorar so e preenchido quando ela pediu apenas os arquivos soltos da
    pasta: e o conjunto de nomes de pasta que a varredura deve pular.
    abrangencia e a frase que o relatorio diz em voz alta nesse caso."""

    caminho: Path
    ignorar: set = None
    abrangencia: str = None


class _Encerrar(Exception):
    """A pessoa saiu do menu (comando s, Ctrl+C ou fim da entrada)."""


def contar_python(pasta, ignorar=PASTAS_IGNORADAS, limite=LIMITE_PASTAS_NA_CONTAGEM):
    """Conta os .py sob pasta com as mesmas regras da analise.

    Devolve (total, completa). completa e False quando a contagem parou no
    limite de pastas visitadas; limite=None conta tudo."""
    total = visitadas = 0
    for _raiz, subpastas, nomes in os.walk(pasta):
        if limite is not None and visitadas >= limite:
            return total, False  # ainda havia pastas por visitar
        subpastas[:] = [s for s in subpastas if s not in ignorar]
        total += sum(1 for nome in nomes if nome.lower().endswith(".py"))
        visitadas += 1
    return total, True


def _e_oculta(entrada) -> bool:
    """Pasta oculta ou de sistema: nome com ponto ou cifrao, ou atributo do Windows."""
    if entrada.name.startswith((".", "$")):
        return True
    try:
        atributos = entrada.stat().st_file_attributes  # so existe no Windows
    except (AttributeError, OSError):
        return False
    return bool(atributos & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM))


def listar_nivel(pasta, ignorar=PASTAS_IGNORADAS,
                 limite=LIMITE_PASTAS_NA_CONTAGEM) -> Nivel:
    """Lista o primeiro nivel de pasta: so subpastas que tem codigo Python.

    Levanta OSError se a pasta nao puder ser aberta."""
    pasta = Path(pasta)
    subpastas, ocultas, soltos = [], 0, 0
    with os.scandir(pasta) as varredura:
        entradas = sorted(varredura, key=lambda e: e.name.lower())
    for entrada in entradas:
        try:
            eh_arquivo = entrada.is_file()
            eh_pasta = entrada.is_dir()
        except OSError:
            continue
        if eh_arquivo:
            if entrada.name.lower().endswith(".py"):
                soltos += 1
        elif eh_pasta:
            if entrada.name in ignorar or _e_oculta(entrada):
                ocultas += 1
                continue
            total, completa = contar_python(entrada.path, ignorar, limite)
            if total == 0 and completa:
                ocultas += 1
                continue
            subpastas.append(Subpasta(entrada.name, Path(entrada.path), total, completa))
    return Nivel(pasta, subpastas, ocultas, soltos)


def _diretos(pasta):
    """Nomes de todas as subpastas diretas e quantidade de .py soltos, sem filtro."""
    subpastas, soltos = [], 0
    with os.scandir(pasta) as varredura:
        for entrada in varredura:
            try:
                if entrada.is_dir():
                    subpastas.append(entrada.name)
                elif entrada.name.lower().endswith(".py") and entrada.is_file():
                    soltos += 1
            except OSError:
                continue
    return subpastas, soltos


def _normalizar(texto: str) -> str:
    """Minusculas, sem acento, sublinhado e hifen como espaco: para filtrar."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFKD", texto)
                         if not unicodedata.combining(c))
    return " ".join(sem_acento.lower().replace("_", " ").replace("-", " ").split())


def _nome(caminho: Path) -> str:
    return falavel(caminho.name) or (caminho.drive or str(caminho))


def _descrever(caminho: Path) -> str:
    """"projeto, dentro de Documentos": onde a pasta fica, sem ler o caminho todo."""
    if caminho.parent != caminho and caminho.parent.name:
        return f"{_nome(caminho)}, dentro de {falavel(caminho.parent.name)}"
    return _nome(caminho)


def _contagem(subpasta: Subpasta) -> str:
    if subpasta.completa:
        return plural(subpasta.arquivos_py, "arquivo Python", "arquivos Python")
    if subpasta.arquivos_py:
        return "pelo menos " + plural(subpasta.arquivos_py, "arquivo Python",
                                      "arquivos Python")
    return "muitos arquivos, nao consegui contar os de Python"


def _motivo(erro: OSError) -> str:
    return erro.strerror or str(erro)


def _parece_caminho(texto: str) -> bool:
    """Caminho completo (colado do Explorador) e nao parte de um nome."""
    limpo = texto.strip("\"'")
    return "\\" in limpo or "/" in limpo or (len(limpo) >= 2 and limpo[1] == ":")


class Navegador:
    """Conversa de uma pergunta por vez que termina numa Escolha, ou em nada."""

    def __init__(self, inicio=None, entrada=None, saida=None, com_explicacao=False):
        self.inicio = Path(inicio) if inicio else None
        self.entrada = entrada or input
        self.saida = saida or print
        self.com_explicacao = com_explicacao
        self.pasta = None
        self.nivel = None
        self.filtro = ""
        self.pagina = 0
        self._avisou_abrangencia = False

    # ---- entrada e saida ------------------------------------------------

    def _dizer(self, *linhas):
        for linha in linhas:
            self.saida(linha)

    def _ler(self, pergunta="Opcao: "):
        try:
            return self.entrada(pergunta).strip()
        except (EOFError, KeyboardInterrupt):
            raise _Encerrar()

    def _sim(self, pergunta):
        return self._ler(pergunta).lower() in ("s", "sim")

    # ---- conversa -------------------------------------------------------

    def executar(self):
        try:
            if self.inicio is None:
                escolha = self._partida_pelos_recentes()
                if escolha is not None:
                    return escolha
            self._abrir_inicial()
            self._mostrar()
            while True:
                escolha = self._tratar(self._ler())
                if escolha is not None:
                    return escolha
        except _Encerrar:
            self._dizer("Encerrado. Nada foi analisado.")
            return None

    def _partida_pelos_recentes(self):
        lista = recentes.carregar()
        if not lista:
            return None
        self._dizer(f"Ultimo projeto analisado: {_descrever(lista[0])}.",
                    "Digite 1 para usar de novo, ou 2 para escolher outra pasta.")
        while True:
            resposta = self._ler()
            if resposta == "1":
                return self._confirmar(lista[0])
            if resposta == "2":
                return None
            self._dizer("Digite 1 ou 2.")

    def _abrir_inicial(self):
        try:
            alvo = self.inicio or Path.cwd()
        except OSError:
            alvo = Path.home()
        for candidato in (alvo, Path.home()):
            try:
                self._abrir(candidato)
                return
            except OSError as erro:
                self._dizer(f"Nao consegui abrir a pasta {_nome(candidato)}: "
                            f"{_motivo(erro)}.")
        self._dizer("Nao consegui abrir nenhuma pasta para comecar. "
                    "Passe o caminho do projeto na linha de comando.")
        raise _Encerrar()

    def _abrir(self, pasta):
        nivel = listar_nivel(pasta)  # pode levantar OSError: nada muda antes disso
        self.pasta, self.nivel = Path(pasta), nivel
        self.filtro, self.pagina = "", 0

    def _ir_para(self, pasta):
        try:
            self._abrir(pasta)
        except OSError as erro:
            self._dizer(f"Nao consegui abrir a pasta {_nome(Path(pasta))}: "
                        f"{_motivo(erro)}. Continuo em {_nome(self.pasta)}.")
            return
        self._mostrar()

    # ---- telas ----------------------------------------------------------

    def _itens(self):
        if not self.filtro:
            return self.nivel.subpastas
        alvo = _normalizar(self.filtro)
        return [s for s in self.nivel.subpastas if alvo in _normalizar(s.nome)]

    def _mostrar(self):
        self._cabecalho()
        self._pagina()
        self._rodape()

    def _cabecalho(self):
        pasta = self.pasta
        if pasta.name:
            onde = f"Voce esta na pasta {_descrever(pasta)}."
        else:
            onde = f"Voce esta na raiz do disco {pasta.drive or pasta}."
        subpastas, soltos = len(self.nivel.subpastas), self.nivel.soltos
        if subpastas:
            quantas = f"Ha {plural(subpastas, 'pasta', 'pastas')} com codigo Python"
        else:
            quantas = "Nao ha subpastas com codigo Python"
        if soltos:
            quantas += (f" e {plural(soltos, 'arquivo Python solto', 'arquivos Python soltos')}"
                        " nesta pasta")
        self._dizer(onde, quantas + ".")

    def _pagina(self):
        itens = self._itens()
        if self.filtro:
            self._dizer(f"Filtro: {self.filtro}. "
                        f"{plural(len(itens), 'pasta encontrada', 'pastas encontradas')}.")
        inicio = self.pagina * POR_TELA
        fim = min(inicio + POR_TELA, len(itens))
        if len(itens) > POR_TELA:
            self._dizer(f"Mostrando de {inicio + 1} a {fim} de {len(itens)}.")
        for numero in range(inicio + 1, fim + 1):
            subpasta = itens[numero - 1]
            self._dizer(f"{numero}, {falavel(subpasta.nome)}, {_contagem(subpasta)}.")

    def _rodape(self, com_ocultas=True):
        if com_ocultas and self.nivel.ocultas and not self.filtro:
            self._dizer(f"Ocultei {plural(self.nivel.ocultas, 'pasta', 'pastas')} "
                        "sem codigo Python ou de sistema.")
        opcoes = []
        if self._itens():
            opcoes.append("o numero para entrar")
        opcoes.append("a para analisar esta pasta")
        if len(self._itens()) > POR_TELA:
            opcoes.append("m para ver mais")
        opcoes.append("v para voltar uma pasta")
        opcoes.append("? para ajuda")
        self._dizer("Digite " + ", ".join(opcoes[:-1]) + " ou " + opcoes[-1] + ".")

    def _ajuda(self):
        self._dizer(
            "Ajuda.",
            "Digite o numero de uma pasta para entrar nela.",
            "A letra a analisa a pasta em que voce esta.",
            "A letra v volta uma pasta.",
            "A letra m mostra mais pastas, quando a lista tem mais de sete.",
            "A letra r mostra os projetos recentes.",
            "A letra l limpa o filtro.",
            "A letra s sai sem analisar.",
            "Digite parte do nome de uma pasta para filtrar a lista.",
            "Voce tambem pode colar o caminho completo de uma pasta.",
            "Enter sozinho repete a tela.")

    # ---- comandos -------------------------------------------------------

    def _tratar(self, texto):
        comando = texto.lower()
        if comando == "":
            self._mostrar()
        elif comando.isdecimal():
            self._entrar_pelo_numero(int(comando))
        elif comando == "a":
            return self._analisar_aqui()
        elif comando == "v":
            self._subir()
        elif comando == "m":
            self._mais()
        elif comando == "r":
            return self._ver_recentes()
        elif comando == "l":
            self._limpar_filtro()
        elif comando == "?":
            self._ajuda()
        elif comando == "s":
            raise _Encerrar()
        elif _parece_caminho(texto):
            return self._ir_para_caminho(texto)
        else:
            self._filtrar(texto)
        return None

    def _entrar_pelo_numero(self, numero):
        itens = self._itens()
        if 1 <= numero <= len(itens):
            self._ir_para(itens[numero - 1].caminho)
        elif itens:
            self._dizer(f"Nao existe a opcao {numero}. Escolha de 1 a {len(itens)}.")
        else:
            self._dizer(f"Nao existe a opcao {numero}: nao ha pastas na lista.")

    def _subir(self):
        pai = self.pasta.parent
        if pai == self.pasta:
            self._dizer("Esta e a raiz do disco, nao ha pasta acima.")
        else:
            self._ir_para(pai)

    def _mais(self):
        itens = self._itens()
        if len(itens) <= POR_TELA:
            self._dizer("Nao ha mais pastas alem das listadas.")
            return
        paginas = -(-len(itens) // POR_TELA)
        self.pagina += 1
        if self.pagina >= paginas:
            self.pagina = 0
            self._dizer("Fim da lista, recomecando do inicio.")
        self._pagina()
        self._rodape(com_ocultas=False)

    def _filtrar(self, texto):
        anterior, self.filtro = self.filtro, texto
        if not self._itens():
            self.filtro = anterior
            self._dizer(f"Nenhuma pasta tem {texto} no nome. A lista continua como estava.")
            return
        self.pagina = 0
        self._pagina()
        self._rodape(com_ocultas=False)

    def _limpar_filtro(self):
        if not self.filtro:
            self._dizer("Nao ha filtro ativo.")
            return
        self.filtro, self.pagina = "", 0
        self._mostrar()

    def _ir_para_caminho(self, texto):
        try:
            caminho = Path(os.path.expanduser(texto.strip("\"'"))).resolve()
        except OSError:
            self._dizer("Nao encontrei esse caminho.")
            return None
        if caminho.is_dir():
            self._ir_para(caminho)
        elif caminho.is_file() and caminho.suffix.lower() == ".py":
            escolha = self._confirmar(caminho)
            if escolha is None:
                self._mostrar()
            return escolha
        elif caminho.exists():
            self._dizer("Esse caminho nao e uma pasta nem um arquivo Python.")
        else:
            self._dizer("Nao encontrei esse caminho.")
        return None

    def _ver_recentes(self):
        lista = recentes.carregar()
        if not lista:
            self._dizer("Ainda nao ha projetos recentes.")
            return None
        self._dizer("Projetos recentes.")
        for numero, caminho in enumerate(lista, start=1):
            self._dizer(f"{numero}, {_descrever(caminho)}.")
        resposta = self._ler("Digite o numero do projeto, ou Enter para voltar. ")
        if resposta.isdecimal() and 1 <= int(resposta) <= len(lista):
            escolha = self._confirmar(lista[int(resposta) - 1])
            if escolha is not None:
                return escolha
        elif resposta:
            self._dizer("Opcao invalida.")
        self._mostrar()
        return None

    # ---- escolha final --------------------------------------------------

    def _analisar_aqui(self):
        escolha = self._confirmar(self.pasta)
        if escolha is None:
            self._mostrar()
        return escolha

    def _confirmar(self, caminho):
        """Diz o que sera analisado e pede confirmacao. None volta ao menu."""
        caminho = Path(caminho)
        nome = _nome(caminho)

        if caminho.is_file():
            self._dizer(f"Vou analisar o arquivo {nome}.")
            self._avisos()
            if not self._sim("Digite s para confirmar, ou Enter para voltar. "):
                return None
            return self._concluir(Escolha(caminho))

        try:
            total, _ = contar_python(caminho, limite=None)
            subpastas, soltos = _diretos(caminho)
        except OSError as erro:
            self._dizer(f"Nao consegui ler a pasta {nome}: {_motivo(erro)}.")
            return None
        if total == 0:
            self._dizer(f"Nao ha arquivos Python na pasta {nome} nem nas suas subpastas.")
            return None

        arquivos = plural(total, "arquivo Python", "arquivos Python")
        if soltos == total or soltos == 0:
            detalhe = "" if soltos == total else ", todos em subpastas"
            self._dizer(f"Vou analisar a pasta {nome}: {arquivos}{detalhe}.")
            self._avisos()
            if not self._sim("Digite s para confirmar, ou Enter para voltar. "):
                return None
            return self._concluir(Escolha(caminho))

        self._dizer(
            f"Pasta {nome}.",
            f"Digite 1 para analisar com as subpastas: {arquivos}.",
            f"Digite 2 para analisar so os arquivos desta pasta: "
            f"{plural(soltos, 'arquivo Python', 'arquivos Python')}.")
        self._avisos()
        while True:
            resposta = self._ler("Digite 1, 2, ou Enter para voltar. ")
            if resposta == "":
                return None
            if resposta == "1":
                return self._concluir(Escolha(caminho))
            if resposta == "2":
                return self._concluir(Escolha(
                    caminho,
                    ignorar=set(PASTAS_IGNORADAS) | set(subpastas),
                    abrangencia=ABRANGENCIA_SOLTOS))
            self._dizer("Digite 1, 2, ou Enter para voltar.")

    def _avisos(self):
        if not self._avisou_abrangencia:
            self._avisou_abrangencia = True
            self._dizer("Atencao: a analise considera so o que esta dentro da escolha. "
                        "Chamadas vindas de fora dela nao aparecem.")
        if self.com_explicacao:
            self._dizer("Com a explicacao do modelo, cada regiao leva de segundos a minutos.")

    def _concluir(self, escolha):
        if escolha.caminho.is_dir():
            erro = recentes.registrar(escolha.caminho)
            if erro:
                self._dizer(erro)
        return escolha


def escolher_pasta(inicio=None, entrada=None, saida=None, com_explicacao=False):
    """Abre o menu de pastas. Devolve uma Escolha, ou None se a pessoa saiu.

    inicio: pasta onde a navegacao comeca (padrao: a pasta atual do
    terminal; sem inicio, o ultimo projeto e oferecido primeiro).
    entrada(pergunta) e saida(linha) padrao: input e print."""
    return Navegador(inicio=inicio, entrada=entrada, saida=saida,
                     com_explicacao=com_explicacao).executar()
