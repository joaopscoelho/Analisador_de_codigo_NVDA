# Analisador de codigo acessivel - prototipo (TCC II)

Prototipo do Trabalho de Conclusao de Curso "Geracao de Explicacoes de Codigo
Baseadas em Inteligencia Artificial com Foco na Identificacao de Pontos
Criticos e Alinhamento a Regra de Negocio para Programadores com Deficiencia
Visual". A monografia, com a arquitetura e as decisoes de projeto, esta na
pasta `Parte escrita` deste repositorio.

## Estado atual

- **Fase 1 (nucleo de analise estatica): funcionando.** Tree-sitter, regras
  de pontos criticos, aviso de erro de sintaxe, varredura de projeto
  inteiro e agrupamento da saida por funcao envolvente.
- **Fase 2, parte deterministica: funcionando.** Mapa estrutural do projeto
  (`analisador/contexto`): definicoes, imports e grafo local de chamadas
  entre arquivos.
- **Fase 2, parte LLM: implementada e testada** com modelo local (`qwen3:8b`)
  e em nuvem (`gemma4:31b`). Ver "O que foi e o que nao foi testado". A API
  do Claude nao foi implementada: o prototipo usa modelos abertos, locais ou
  hospedados no Ollama.
- **Fase 4, fala via NVDA (so Windows): implementada e testada com o NVDA
  real.** Ver "Fala via NVDA (Windows)".
- **Comando `analisar` e menu de pastas (Fase 4, primeira parte):
  funcionando.** A pessoa entra na pasta do projeto com `cd` e digita
  `analisar`: sem caminho, vale a pasta atual. O `instalar_comando.ps1` deixa
  o comando disponivel em qualquer pasta do Windows, e `--menu` escolhe a
  pasta por um menu, um nivel por vez. Coberto por testes; o comando foi
  testado com o NVDA real e o menu, no Windows; **nenhum dos dois foi testado
  por uma pessoa cega** (ver "Comando analisar (Windows)" e "O que foi e o
  que nao foi testado").
- Fase 3 (verificacao automatica das explicacoes) e navegacao pelos
  resultados (proxima regiao, repetir, explicacao sob demanda): nao
  implementadas.

O escopo de analise e o **projeto inteiro**, nao um arquivo isolado.

## Como rodar

Windows (PowerShell):

```powershell
cd prototipo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH = "."
pytest testes/ -v
```

Se a pasta `.venv` ja existir e tiver sido criada em Linux ou macOS (tem
`bin/` em vez de `Scripts/`), apague-a antes: ela e ignorada pelo git e o
Windows nao a usa.

Atalho no Windows: `powershell -ExecutionPolicy Bypass -File .\preparar_windows.ps1`
faz os passos acima (acha o Python mesmo sem PATH), roda os testes, confere o
NVDA e a DLL e grava tudo em `preparar_windows.log`. Com `-Falar`, o NVDA
fala uma frase de teste.

macOS ou Linux (nao testado):

```bash
cd prototipo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest testes/ -v
```

Analise estatica (sem modelo, sem rede):

```bash
PYTHONPATH=. python -m analisador caminho/do/projeto
PYTHONPATH=. python -m analisador caminho/do/projeto --json
```

Para guardar o relatorio em arquivo, use `--saida` em vez de `>`:

```powershell
python -m analisador caminho\do\projeto --explicar --saida saida_relatorio.txt
```

O `>` do PowerShell regrava a saida com a pagina de codigo do console e
estraga os acentos ("Inferência" vira "Infer├¬ncia"); `--saida` grava em UTF-8
direto do Python. Arquivos `saida_*` ficam fora do git.

## Comando analisar (Windows)

O jeito mais simples de usar: entrar na pasta do projeto e digitar so o
comando. Sem caminho, a pasta atual do terminal e analisada.

Uma vez so, na pasta `prototipo`, depois do `preparar_windows.ps1`:

```powershell
powershell -ExecutionPolicy Bypass -File .\instalar_comando.ps1
```

O script acrescenta a pasta `prototipo` ao PATH do seu usuario, sem pedir
administrador; rodar de novo nao duplica a entrada, e `-Remover` desfaz.
Feche o terminal e abra um novo (no VS Code, feche e abra o VS Code). A
partir dai, de qualquer pasta:

```powershell
cd Documents\meu_projeto
analisar                        # analisa a pasta atual
analisar --falar                # e fala o relatorio pelo NVDA
analisar --explicar             # com a explicacao do modelo
analisar caminho\do\projeto     # analisa outra pasta, sem sair desta
analisar --menu                 # escolhe a pasta por um menu
```

Sem instalar, o mesmo atalho funciona de dentro da pasta `prototipo`:
`.\analisar caminho\do\projeto`. O `analisar.cmd` usa o `.venv` sozinho,
dispensa o `PYTHONPATH` e liga o `PYTHONSAFEPATH` (Python 3.11 ou mais novo),
para que um arquivo do projeto analisado, como um `json.py`, nao rode no
lugar de uma biblioteca do Python.

Na pasta pessoal, onde todo terminal novo abre, e na raiz do disco,
`analisar` sem caminho nao analisa nada e diz como seguir: a varredura
passaria por arquivos de fora do projeto. Para analisar uma delas mesmo
assim, informe o caminho (`analisar .`). Caminho que nao existe e arquivo
que nao e `.py` tambem sao ditos em palavras, com codigo de saida 1, e uma
pasta sem Python gera o aviso "Nenhum arquivo Python foi encontrado", sem
chamar o modelo.

Em macOS e Linux (nao testado) nao ha instalador: rode da pasta `prototipo` com
`PYTHONPATH=. python -m analisador caminho/do/projeto`, ou com `--menu`.

### Menu de pastas (`--menu`)

Para quem prefere escolher a pasta sem digitar caminho. `analisar --menu`
comeca na pasta atual e oferece primeiro o ultimo projeto analisado pelo
menu; `analisar --menu caminho` comeca na pasta indicada. `--menu` nao se
combina com `--json`.

Cada tela diz onde a pessoa esta, quantas pastas com codigo Python existem ali
e lista no maximo sete, numeradas. Pastas sem Python e pastas de ferramenta
(.venv, .git, node_modules) ficam de fora, e a tela diz quantas foram
ocultadas. Comandos:

- numero: entra na pasta (na segunda tela a numeracao continua: 8, 9...)
- a: analisa a pasta atual. Se houver subpastas com codigo, pergunta se e a
  pasta inteira ou so os arquivos soltos nela
- v: volta uma pasta. m: mostra mais. r: projetos recentes. l: limpa o filtro
- parte de um nome: filtra a lista, sem diferenciar acento nem maiuscula
- caminho completo colado (no Explorador, "Copiar como caminho"): vai direto
- Enter sozinho: repete a tela. ?: ajuda. s: sai sem analisar

Na partida, se ja houve uma analise pelo menu, o ultimo projeto e oferecido
(1 para usar de novo, 2 para escolher outra pasta). A lista de recentes fica
em `%APPDATA%\analisador\recentes.json` (ou na pasta da variavel
`ANALISADOR_CONFIG`), fora do projeto.

## Explicacao com modelo local (Ollama)

1. Instalar o Ollama (ollama.com) e abrir o aplicativo.
2. Baixar o modelo padrao, pensado para 16 GB de memoria:

```bash
ollama pull qwen3:8b
```

3. Rodar com `--explicar`:

```bash
PYTHONPATH=. python -m analisador caminho/do/projeto --explicar
PYTHONPATH=. python -m analisador caminho/do/projeto --explicar --modelo qwen3:14b
PYTHONPATH=. python -m analisador caminho/do/projeto --explicar --max-regioes 3
```

Cada explicacao leva de segundos a minutos no hardware local; o progresso
vai para a saida de erro ("Gerando explicacao 2 de 5..."). Se o Ollama nao
estiver no ar ou o modelo nao tiver sido baixado, o erro e dito em palavras,
a analise estatica e entregue mesmo assim e o codigo de saida e 2.

Opcoes: `--modelo`, `--host`, `--contexto` (padrao 8192 tokens),
`--max-regioes`. Tambem valem as variaveis `ANALISADOR_MODELO` e
`OLLAMA_HOST`.

Modelos candidatos para 16 GB (tamanhos segundo a biblioteca do Ollama;
confira com `ollama list`):

- `qwen3:8b` - padrao. Cabe com folga, treinado em 119 idiomas.
- `qwen3:14b` - mais qualidade, ocupa mais memoria.
- `gpt-oss:20b` - cerca de 14 GB: cabe no papel, mas deixa pouca folga para
  o sistema, e avaliacao independente (Bi et al., 2025, arXiv:2508.12461)
  aponta fraqueza fora do ingles.

## Modelo em nuvem (Ollama cloud)

Alem dos modelos locais, o mesmo cliente chama modelos hospedados no
ollama.com, como o `gemma4:31b`. A pagina do modelo lista tambem as tags
`gemma4:cloud` e `gemma4:31b-cloud`. **O codigo analisado sai do seu
computador neste modo.** A documentacao do Ollama diz que prompts e respostas
da nuvem nao sao usados para treinar modelos e nao informa prazo de retencao.
Use com codigo de exemplo, nunca com codigo privado: o argumento de
privacidade da execucao local nao vale para este modo.

1. Crie uma chave de API em ollama.com/settings/keys.
2. Defina a chave so na sessao do terminal. Nunca no codigo, em arquivo
   versionado ou em conversa:

```powershell
$env:OLLAMA_API_KEY = "cole-a-chave-aqui"
```

3. Confira o nome exato do modelo na lista do servidor e rode:

```powershell
(Invoke-RestMethod https://ollama.com/api/tags).models.name | Select-String gemma
python -m analisador caminho\do\projeto --explicar --host https://ollama.com --modelo gemma4:31b
```

A chave so e enviada ao host `ollama.com`. Sem a chave o erro aparece na hora,
e uma chave recusada (401 ou 403) interrompe a geracao. Na API direta o nome do
modelo e o da lista do servidor (`gemma4:31b`); no aplicativo ou na CLI do
Ollama instalado o sufixo e `:cloud` (`gemma4:31b-cloud`). O uso e cobrado
por token (ollama.com/pricing); sem creditos, o servidor recusa as
requisicoes com o erro 402.

## Fala via NVDA (Windows)

Requisitos: Windows, Python e NVDA com a mesma arquitetura da DLL, NVDA
instalado e a DLL `nvdaControllerClient.dll` do NV Access (LGPL 2.1, por isso
fora do git). Passo a passo em `bibliotecas/LEIA-ME.md`.

```powershell
analisar --falar                    # na pasta do projeto
analisar caminho\do\projeto --explicar --falar
analisar --falar --dll C:\outro\nvdaControllerClient.dll
```

O relatorio e impresso como sempre e tambem enviado ao NVDA em uma unica
chamada. O NVDA e conferido **antes** da analise e do modelo, para o erro
aparecer em segundos. Se o NVDA, a DLL ou o Windows faltarem, o erro e
dito em palavras, o relatorio sai so como texto e o codigo de saida e 3
(codigo 2 continua sendo falha do modelo e tem prioridade). `--falar` nao
se combina com `--json`. Com `--falar`, o aviso de pasta errada tambem e
falado.

Se o NVDA estiver instalado mas fechado, `--falar` o abre e espera ate 20
segundos que ele responda, dizendo em palavras o que esta fazendo ("Abrindo
o NVDA, aguarde...", "NVDA aberto."). O `nvda.exe` e procurado em
`Program Files\NVDA` e `Program Files (x86)\NVDA`; para um NVDA portatil,
indique o caminho na variavel `NVDA_EXE`. Se o Windows indicar que outro
leitor de tela esta ativo, o NVDA nao e aberto, para nao falarem duas vozes.

Fora do Windows nao ha falador: o NVDA nao existe em macOS nem em Linux.
A interface `Falador` (`analisador/nvda/base.py`) deixa espaco para outro
sistema de fala, ainda nao implementado.

## O que foi e o que nao foi testado

Coberto por testes automatizados (198 testes, que nao dependem de modelo,
rede, NVDA nem Windows): analise estatica, grafo de chamadas, montagem dos
prompts, orquestracao, politica de falhas, CLI (com um LLM falso), analise da
pasta atual e avisos de caminho errado, e menu de pastas (com entrada falsa);
cliente do Ollama contra um servidor HTTP falso que reproduz o formato
documentado da API; falador do NVDA contra uma DLL falsa, busca da DLL e
opcao `--falar` da CLI com um falador falso; chave de API da nuvem enviada
so ao host `ollama.com`. A suite atual ainda nao foi executada e registrada.
O registro disponivel, no Windows e com uma versao anterior da suite, tem 114
testes aprovados e 1 ignorado, alem da falha de um teste sensivel ao tempo de
conexao, cujo limite foi ajustado em seguida.

**Testado no Windows:**

- `analisar --falar` na pasta do projeto de exemplo: o relatorio foi impresso
  e falado pelo NVDA. A DLL x64 carregou e `testIfRunning` respondeu com o
  NVDA aberto.
- `analisar` sem caminho, dentro da pasta do projeto: a pasta atual foi
  analisada.
- Menu de pastas, aberto pelo `analisar.cmd`.
- Explicacao com modelo local (`qwen3:8b`): visao geral e quatro regioes.
- Explicacao em nuvem (`gemma4:31b`, projeto de exemplo, duas regioes): 3,06
  segundos no total, com o campo `think: false` aceito. Sem creditos de uso,
  o servidor recusa as requisicoes (erro 402).
- Modelo ausente: a verificacao inicial informa o erro em palavras e lista os
  modelos instalados.
- Abertura automatica do NVDA: por CreateProcess, o Windows recusou com o erro
  740 ("A operacao solicitada requer elevacao"); pelo ShellExecute, como um
  atalho, o NVDA abriu e respondeu. Em uma das execucoes com abertura
  automatica, o NVDA nao aceitou o texto para falar; o erro foi dito em
  palavras e o relatorio saiu so como texto.

**Nao testado:**

- Uso por uma pessoa cega: comando, menu e explicacoes. A pasta atual como
  padrao, sete itens por tela, texto sem acento e uma pergunta por vez sao
  decisoes de projeto, nao resultados.
- Menu de pastas com o NVDA falando.
- Versao do NVDA; limite de tamanho do texto em uma chamada; chamadas
  seguidas; fala duplicada quando o terminal imprime o mesmo texto; Windows
  bloqueado. O prototipo nao confere se o Windows esta bloqueado, como
  recomenda a documentacao do NV Access.
- Indicador de outro leitor de tela ativo (so com testes simulados).
- Formato real do erro de chave recusada (401 ou 403).
- Campo `think: "low"` (familia gpt-oss).
- Qualidade das explicacoes medida de forma sistematica e comparacao entre
  modelos. Nos textos examinados, os modelos mantiveram o marcador de
  inferencia, mas escreveram nomes de funcao com sublinhado e fizeram
  afirmacoes sem respaldo nos dados enviados, como uma divisao por zero que
  nao existe no codigo. A medicao sistematica depende da Fase 3, nao
  implementada.

## Estrutura

```
analisador/
  parser/
    ast_parser.py     AST via Tree-sitter, helpers e erros de sintaxe
    varredura.py      descoberta e parse de todos os .py do projeto
  pontos_criticos/
    regras.py         regras deterministicas (lista fechada, secao 8)
    agrupamento.py    agrupa os pontos por funcao envolvente
  contexto/
    estrutura.py      definicoes, imports e chamadas de um arquivo
    mapa.py           MapaProjeto: grafo de chamadas e contexto por linha
    trechos.py        codigo da regiao, com numero de linha, para o prompt
  llm/
    base.py           interface ExplicadorLLM, mensagens, erros
    prompts.py        prompt de visao geral e prompt por regiao
    local.py          ExplicadorLocal: Ollama, sem dependencia nova
  analise.py          orquestracao: parser + contexto + regras
  explicacao.py       orquestracao: visao geral + uma explicacao por regiao
  __main__.py         runner da linha de comando: analisar [caminho] [opcoes]
  formatacao/         reservado para a Fase 3 (vazio)
  nvda/
    base.py           interface Falador e erros
    cliente.py        NvdaFalador: ctypes sobre o nvdaControllerClient.dll
  cli/                Fase 4 - menu de pastas (navegacao pelos resultados: vazio)
    navegador.py      menu: um nivel por vez, filtro, escopo, confirmacao
    recentes.py       ultimos projetos analisados pelo menu
    texto.py          concordancia e nomes falaveis
analisar.cmd          atalho do Windows: usa o .venv e chama o analisador
instalar_comando.ps1  poe a pasta prototipo no PATH do usuario (-Remover desfaz)
preparar_windows.ps1  prepara o .venv, roda os testes e confere o NVDA
bibliotecas/          nvdaControllerClient.dll, baixada a parte (fora do git)
testes/
  conftest.py                    fixtures e servidor Ollama falso
  ollama_falso.py                servidor HTTP falso (formato documentado)
  test_parser.py                 parse, erro de sintaxe, varredura
  test_pontos_criticos.py        regras e filtros de falso positivo
  test_contexto.py               definicoes, imports, grafo, regressoes
  test_agrupamento.py            reducao de ruido na saida
  test_analise.py                ponta a ponta e formato do relatorio
  test_llm_local.py              cliente do Ollama e traducao de erros
  test_prompts.py                conteudo dos prompts
  test_explicacao.py             orquestracao e CLI com LLM falso
  test_nvda.py                   falador do NVDA com DLL falsa e CLI --falar
  test_navegador.py              menu de pastas, recentes e --saida
  test_comando.py                pasta atual, caminho errado, atalho .cmd e instalador
  fixtures/
    exemplo_funcionarios.py      fixture original, arquivo unico
    projeto_exemplo/             tres arquivos que se importam (secao 12)
    projeto_quebrado/            arquivo invalido de proposito
```

## Decisoes registradas

- **Erro de sintaxe e reportado, nao ignorado.** O Tree-sitter devolve
  arvore parcial para codigo invalido; sem o aviso, a ferramenta analisaria
  um arquivo incompleto em silencio. Como o publico-alvo nao enxerga a tela
  do editor, esse aviso e requisito, nao detalhe.
- **Verbos ambiguos exigem evidencia.** `get`, `post`, `save` e `query` so
  contam como dependencia externa em arquivos que importam biblioteca de
  rede ou de banco. Rodar o analisador sobre o proprio prototipo mostrou
  todo `dicionario.get` classificado como dependencia externa de severidade
  5: falso positivo que destroi a confianca na lista.
- **Literais triviais sao filtrados.** `0`, `1`, `None` e comparacao com
  booleano sao idiomas da linguagem, nao regra de negocio.
- **A saida e agrupada por funcao, nao achatada.** Nenhum ponto e
  descartado no agrupamento.
- **Resolucao de chamadas por nome simples.** Sem inferencia de tipos, a
  prioridade e o proprio arquivo e depois os arquivos importados; casos
  ambiguos ficam registrados em `MapaProjeto.ambiguas`.
- **Codigo de modulo tem chave propria no grafo.** Chamadas fora de qualquer
  funcao eram guardadas como `None`, o que quebrava a ordenacao
  (`TypeError`) quando uma funcao era chamada por outra funcao e pelo
  modulo. Chamadas de modulo (`if __name__ == "__main__": main()`) nao
  contam como chamador ao decidir pontos de entrada, e metodos como
  `__init__` nunca sao pontos de entrada.
- **API nativa do Ollama, nao o endpoint compativel com a OpenAI.** A
  documentacao do Ollama afirma que a API da OpenAI nao tem como definir o
  tamanho de contexto, e o padrao do Ollama abaixo de 24 GiB e 4k tokens.
  A API nativa aceita `num_ctx`, `seed` e `temperature` por requisicao.
- **Prompt grande demais e recusado, nao truncado.** O cliente estima os
  tokens e recusa o que nao cabe no contexto configurado; a documentacao
  nao descreve o que o Ollama faz com um prompt que excede o contexto.
- **Dois tipos de falha.** Erro de configuracao (servidor fora do ar,
  modelo ausente) interrompe tudo na hora; erro isolado (resposta vazia,
  tempo esgotado) afeta so a regiao, que e declarada sem explicacao em vez
  de omitida.
- **Regras de acessibilidade no prompt, nao so no pos-processamento.**
  Pedir a forma certa de primeira produz texto melhor que limpar texto
  errado depois. A Fase 3, nao implementada, conferiria se o modelo obedeceu.
- **Inferencia tem marcador fixo.** Regra de negocio deduzida de nomes abre
  com a palavra "Inferência:". Quem ouve por sintese de voz nao consegue
  ver que algo e suposicao; precisa ouvir. Por ser palavra fixa, a Fase 3
  pode verificar a marcacao automaticamente.
- **Fala conferida antes, falha dita em palavras.** O NVDA e verificado
  antes da analise. Sem DLL, sem Windows ou sem NVDA aberto nao ha
  substituto silencioso: quem usa sem ver a tela nao perceberia que nada
  foi falado. O texto sai impresso de qualquer forma.
- **Reprodutibilidade.** Temperatura zero e semente fixa, registradas junto
  com o digest do modelo no `--json`. Nao garante saida identica entre
  versoes do Ollama ou hardwares diferentes.
- **Sem caminho, vale a pasta atual; o menu e opcional.** A primeira versao
  abria o menu sempre que faltava o caminho e, como o atalho so funcionava de
  dentro da pasta `prototipo`, o menu comecava sempre nela. O autor avaliou
  esse passo obrigatorio como pouco pratico: quem ja esta na
  pasta do projeto, ou sabe o caminho, so precisa do comando. O menu ficou em
  `--menu`, para quem prefere escolher sem digitar caminho.
- **Pasta pessoal e raiz do disco so com pedido explicito.** Todo terminal
  novo abre na pasta pessoal; analisa-la por engano varreria arquivos de
  fora do projeto, e a pessoa ouviria um relatorio longo sobre outra coisa.
  Com o caminho informado (`analisar .`), a analise acontece.
- **Pasta sem Python nao vira "nenhum ponto critico".** Com a pasta atual
  como padrao, rodar na pasta errada e o engano mais provavel, e "Nenhum
  ponto critico encontrado" soaria como codigo sem problema. O relatorio diz
  que nao achou arquivo Python, e o modelo nem e chamado.
- **O projeto analisado nao roda codigo dentro da ferramenta.** Com
  `python -m`, o Python poe a pasta atual na frente das bibliotecas, e um
  `json.py` do projeto rodaria no lugar do `json` padrao. Como o comando
  agora roda de dentro do projeto, o `analisar.cmd` liga o `PYTHONSAFEPATH`;
  um teste confere a protecao e mostra o problema sem ela.
- **O instalador muda so o PATH do usuario e preserva o que ja estava la.**
  Sem administrador. O PATH e lido do registro sem expandir variaveis
  (`%USERPROFILE%`) e regravado com o mesmo tipo; rodar de novo nao duplica,
  e `-Remover` desfaz.
- **Menu de pastas: um nivel por vez, nunca a arvore.** Quem ouve uma
  arvore inteira nao consegue "passar o olho": a tela diz onde a pessoa esta,
  quantas pastas com codigo existem ali e lista no maximo sete. O que e
  ocultado (sem Python, de sistema, de ferramenta) tem a contagem dita em
  voz alta, para ninguem achar que a pasta nao existe.
- **O menu e feito de linhas simples, nao de tela.** So `input()` e `print()`:
  sem limpar a tela, sem cores, sem teclas especiais, que leitores de tela
  tratam mal. O NVDA fala o que o terminal imprime, entao o menu nao usa a
  DLL; ela continua so para o relatorio (`--falar`). Isso tambem deixa o menu
  utilizavel com outros leitores de tela.
- **Escopo dito antes de analisar.** Analisar so uma subpasta perde as
  chamadas que vem de fora dela. O menu avisa uma vez por sessao, e o
  relatorio diz "Escopo: ..." quando a pessoa pediu so os arquivos soltos.
- **Gravar com `--saida`, nao com `>`.** Os acentos de `saida_gemma4.json`
  estao corrompidos (UTF-8 lido como cp850 e regravado), padrao tipico do
  redirecionamento do PowerShell. O Python grava o arquivo em UTF-8 direto.
- **O relatorio diz o nome da pasta, nao o caminho.** "Analise de ." seria
  falado como "analise de ponto"; o nome vem sem sublinhado e sem hifen.
- **NVDA aberto pela ferramenta, mas nunca por cima de outro leitor.** Quem
  usa leitor de tela ja tem um aberto para digitar o comando. O NVDA fechado
  costuma ser outro caso: alguem que enxerga demonstrando a ferramenta, ou um
  NVDA que fechou. Por isso `--falar` abre o NVDA so quando o Windows nao
  indica outro leitor de tela ativo, e os testes nunca abrem o NVDA real.
