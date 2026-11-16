"""
Fala via NVDA: wrapper em ctypes do nvdaControllerClient.dll (metodo 4.5.1
do TCC original).

O NVDA Controller Client e uma biblioteca do proprio NV Access que envia
texto ao NVDA em execucao. Ela e distribuida a parte (arquivo
controllerClient.zip das versoes do NVDA) sob LGPL 2.1, por isso a DLL nao
vai para o repositorio: ver bibliotecas/LEIA-ME.md.

Decisoes:
- A DLL precisa ter a mesma arquitetura do Python em uso (x64 com Python 64
  bits, por exemplo). O carregamento diz isso em palavras quando falha.
- So as funcoes antigas e estaveis sao usadas (testIfRunning, speakText,
  cancelSpeech). As mais novas (como speakSsml) falham com NVDA antigo.
- Sem DLL, sem Windows ou sem NVDA aberto o erro e dito em palavras, nunca
  silenciado: quem usa a ferramenta sem ver a tela nao teria como perceber
  que o texto nao foi falado.
- NVDA instalado mas fechado: o falador o abre e espera ate
  TEMPO_MAXIMO_ABERTURA_S segundos, dizendo em palavras o que esta fazendo.
  Quem usa leitor de tela ja tem um aberto para digitar o comando, entao o
  caso mais comum e outro: alguem que enxerga demonstrando a ferramenta, ou
  um NVDA que fechou. Por isso a abertura nunca acontece se o Windows indica
  outro leitor de tela ativo (indicador SPI_GETSCREENREADER): duas vozes
  falando juntas atrapalham mais do que ajudam.
- Nao ha fala por outro programa: se nada der certo, o falador falha e a
  CLI entrega o texto de qualquer forma.
"""
import ctypes
import os
import platform
import struct
import sys
import time
from pathlib import Path

from analisador.nvda.base import ErroFala, ErroFaladorIndisponivel, Falador

NOME_DLL = "nvdaControllerClient.dll"
VARIAVEL_DLL = "NVDA_CONTROLLER_DLL"
PASTA_BIBLIOTECAS = Path(__file__).resolve().parents[2] / "bibliotecas"

FUNCOES = (
    "nvdaController_testIfRunning",
    "nvdaController_speakText",
    "nvdaController_cancelSpeech",
)

#: Codigo do Windows que a DLL devolve quando o NVDA nao esta em execucao.
RPC_S_SERVER_UNAVAILABLE = 1722
VARIAVEL_NVDA = "NVDA_EXE"
TEMPO_MAXIMO_ABERTURA_S = 20
INTERVALO_VERIFICACAO_S = 0.5
SPI_GETSCREENREADER = 0x0046


class ErroDllNaoEncontrada(ErroFaladorIndisponivel):
    """A nvdaControllerClient.dll nao esta onde a ferramenta procurou."""


def _e_windows() -> bool:
    return sys.platform == "win32"


def _exigir_windows():
    if not _e_windows():
        raise ErroFaladorIndisponivel(
            "O NVDA so existe no Windows: neste sistema "
            f"({sys.platform}) a fala via NVDA nao esta disponivel.")


def arquitetura_python() -> str:
    """Arquitetura do Python em uso: x64, x86 ou arm64 (nome das pastas do zip)."""
    if platform.machine().lower() in ("arm64", "aarch64"):
        return "arm64"
    return "x64" if struct.calcsize("P") == 8 else "x86"


def localizar_dll(caminho=None) -> Path:
    """Acha a DLL: caminho dado, variavel de ambiente ou pasta bibliotecas.

    Um caminho dado de forma explicita (argumento ou variavel) nunca cai em
    outro lugar: se estiver errado, o erro aponta para ele. Sem caminho
    explicito, procura em bibliotecas/ e em bibliotecas/<arquitetura>/.
    """
    explicito = caminho or os.environ.get(VARIAVEL_DLL)
    if explicito:
        candidatos = [Path(explicito)]
    else:
        candidatos = [PASTA_BIBLIOTECAS / NOME_DLL,
                      PASTA_BIBLIOTECAS / arquitetura_python() / NOME_DLL]

    for candidato in candidatos:
        if candidato.is_file():
            return candidato

    procurado = "; ".join(str(c) for c in candidatos)
    raise ErroDllNaoEncontrada(
        f"A biblioteca {NOME_DLL} nao foi encontrada. Procurei em: {procurado}. "
        "Baixe o arquivo controllerClient.zip das versoes do NVDA, extraia e "
        f"copie o {NOME_DLL} da pasta {arquitetura_python()} para "
        f"{PASTA_BIBLIOTECAS}, ou indique o caminho com --dll ou com a "
        f"variavel {VARIAVEL_DLL}.")


def carregar_biblioteca(caminho):
    """Carrega a DLL e declara os tipos das funcoes usadas."""
    _exigir_windows()
    try:
        dll = ctypes.WinDLL(str(caminho))
    except OSError as erro:
        raise ErroFaladorIndisponivel(
            f"Nao foi possivel carregar {caminho}: {erro}. A biblioteca "
            "precisa ter a mesma arquitetura do Python em uso "
            f"({arquitetura_python()}).") from erro

    for nome in FUNCOES:
        if not hasattr(dll, nome):
            raise ErroFaladorIndisponivel(
                f"A biblioteca {caminho} nao oferece a funcao {nome}: o "
                f"arquivo nao parece ser o {NOME_DLL} do NVDA.")

    # error_status_t e um codigo de erro do Windows: 0 e sucesso.
    for nome in FUNCOES:
        getattr(dll, nome).restype = ctypes.c_ulong
    dll.nvdaController_testIfRunning.argtypes = []
    dll.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
    dll.nvdaController_cancelSpeech.argtypes = []
    return dll


def _descrever_codigo(codigo: int) -> str:
    """Codigo de erro do Windows com a mensagem do sistema, quando existir."""
    formatar = getattr(ctypes, "FormatError", None)  # so existe no Windows
    mensagem = ""
    if formatar is not None:
        try:
            mensagem = formatar(codigo).strip()
        except (OSError, ValueError, OverflowError):
            mensagem = ""
    return f"erro {codigo}: {mensagem}" if mensagem else f"erro {codigo}"


def candidatos_nvda(caminho=None):
    """Onde o nvda.exe e procurado: caminho dado, variavel NVDA_EXE ou as
    pastas padrao de instalacao (as mesmas do preparar_windows.ps1)."""
    explicito = caminho or os.environ.get(VARIAVEL_NVDA)
    if explicito:
        return [Path(explicito)]
    bases = (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"))
    return [Path(base) / "NVDA" / "nvda.exe" for base in bases if base]


def localizar_nvda(caminho=None):
    """Caminho do nvda.exe instalado, ou None."""
    for candidato in candidatos_nvda(caminho):
        if candidato.is_file():
            return candidato
    return None


def abrir_nvda(executavel):
    """Abre o NVDA pelo mesmo caminho de um atalho da area de trabalho.

    O nvda.exe instalado tem acesso especial a interface (uiAccess) no
    manifesto, e o Windows recusa abri-lo por CreateProcess, que e o que o
    subprocess usa: erro 740, "A operacao solicitada requer elevacao"
    (observado em 08/11/2026). O ShellExecute, usado pelo os.startfile, e o
    caminho dos atalhos. O NVDA continua aberto depois que a ferramenta
    termina."""
    _exigir_windows()
    os.startfile(str(executavel))


def outro_leitor_de_tela_ativo() -> bool:
    """True se o Windows indica um leitor de tela ativo (SPI_GETSCREENREADER).

    Leitores de tela ligam esse indicador ao iniciar. Se ele esta ligado e o
    NVDA nao responde, quem fala e outro leitor, ou um NVDA que travou."""
    if not _e_windows():
        return False
    valor = ctypes.c_int(0)
    try:
        ok = ctypes.windll.user32.SystemParametersInfoW(
            SPI_GETSCREENREADER, 0, ctypes.byref(valor), 0)
    except (AttributeError, OSError):
        return False
    return bool(ok) and bool(valor.value)


def _avisar_no_terminal(texto):
    print(texto, file=sys.stderr, flush=True)


class NvdaFalador(Falador):
    """Fala o texto pelo NVDA que esta em execucao neste computador.

    biblioteca existe para os testes: qualquer objeto com as tres funcoes
    de FUNCOES substitui a DLL, e entao nada exige Windows nem NVDA.

    abrir_automaticamente: com o NVDA fechado, abri-lo e esperar que
    responda. O padrao (None) liga a abertura so com a DLL de verdade, para
    que os testes nunca abram o NVDA real, mesmo quando rodam no Windows.
    localizar, abrir, leitor_ativo, esperar, relogio e avisar existem para
    os testes substituirem o sistema.
    """

    def __init__(self, caminho_dll=None, biblioteca=None, abrir_automaticamente=None,
                 caminho_nvda=None, localizar=None, abrir=None, leitor_ativo=None,
                 esperar=None, relogio=None, avisar=None,
                 tempo_maximo=TEMPO_MAXIMO_ABERTURA_S):
        self._caminho = None
        dll_real = biblioteca is None
        if dll_real:
            _exigir_windows()
            self._caminho = localizar_dll(caminho_dll)
            biblioteca = carregar_biblioteca(self._caminho)
        self._dll = biblioteca
        self._abrir_automaticamente = (dll_real if abrir_automaticamente is None
                                       else abrir_automaticamente)
        self._caminho_nvda = caminho_nvda
        self._localizar = localizar or localizar_nvda
        self._abrir = abrir or abrir_nvda
        self._leitor_ativo = leitor_ativo or outro_leitor_de_tela_ativo
        self._esperar = esperar or time.sleep
        self._relogio = relogio or time.monotonic
        self._avisar = avisar or _avisar_no_terminal
        self._tempo_maximo = tempo_maximo

    def verificar(self) -> None:
        codigo = self._dll.nvdaController_testIfRunning()
        if codigo == 0:
            return
        if codigo == RPC_S_SERVER_UNAVAILABLE and self._abrir_automaticamente:
            self._abrir_e_esperar()
            return
        raise ErroFaladorIndisponivel(
            f"Nao foi possivel falar com o NVDA ({_descrever_codigo(codigo)}). "
            "Confira se o NVDA esta aberto e com a fala ligada.")

    def _abrir_e_esperar(self):
        if self._leitor_ativo():
            raise ErroFaladorIndisponivel(
                "O NVDA nao esta aberto, e o Windows indica que outro leitor de tela "
                "esta ativo (ou um NVDA que travou). Para nao falarem dois leitores ao "
                "mesmo tempo, o NVDA nao foi aberto automaticamente.")
        executavel = self._localizar(self._caminho_nvda)
        if executavel is None:
            procurado = "; ".join(str(c) for c in candidatos_nvda(self._caminho_nvda))
            raise ErroFaladorIndisponivel(
                "O NVDA nao esta aberto, e nao achei o nvda.exe"
                + (f" em: {procurado}" if procurado else "") + ". Abra o NVDA ou "
                f"indique o caminho do nvda.exe na variavel {VARIAVEL_NVDA}.")
        self._avisar("O NVDA nao estava aberto. Abrindo o NVDA, aguarde ate "
                     f"{self._tempo_maximo} segundos.")
        try:
            self._abrir(executavel)
        except OSError as erro:
            raise ErroFaladorIndisponivel(
                f"Nao consegui abrir o NVDA em {executavel}: {erro.strerror or erro}.") from erro
        limite = self._relogio() + self._tempo_maximo
        while self._relogio() < limite:
            self._esperar(INTERVALO_VERIFICACAO_S)
            if self._dll.nvdaController_testIfRunning() == 0:
                self._avisar("NVDA aberto.")
                return
        raise ErroFaladorIndisponivel(
            f"O NVDA foi aberto, mas nao respondeu em {self._tempo_maximo} segundos. "
            "Espere ele terminar de carregar e rode o comando de novo.")

    def falar(self, texto: str) -> None:
        if not texto or not texto.strip():
            return
        codigo = self._dll.nvdaController_speakText(texto)
        if codigo != 0:
            raise ErroFala(
                f"O NVDA nao aceitou o texto para falar ({_descrever_codigo(codigo)}).")

    def cancelar(self) -> None:
        codigo = self._dll.nvdaController_cancelSpeech()
        if codigo != 0:
            raise ErroFala(
                f"O NVDA nao conseguiu interromper a fala ({_descrever_codigo(codigo)}).")

    def descricao(self) -> dict:
        return {"backend": "nvda",
                "dll": str(self._caminho) if self._caminho else None}
