# Roteiro da defesa do TCC

**Trabalho:** Geração de Explicações de Código Baseadas em Inteligência Artificial com Foco na Identificação de Pontos Críticos e Alinhamento à Regra de Negócio para Programadores com Deficiência Visual
**Autor:** João Pedro Silva Coelho
**Orientadora:** Adriana Zanella Martinhago
**Tempo:** no máximo 40 minutos (Regulamento, Art. 26). Este roteiro soma 35 minutos e deixa 5 de folga. Se o tempo estourar, o presidente da banca pode interromper.

> Trechos entre colchetes, como [resultado da comparação], dependem de etapas que ainda não foram feitas. Preencha quando tiver o resultado ou use a alternativa indicada no próprio bloco. Não apresente número que não esteja registrado.

## Tempo por bloco

| # | Bloco | Slides | Tempo | Acumulado |
|---|---|---|---|---|
| 1 | Abertura | 1 | 1 min | 1 min |
| 2 | Problema e motivação | 2 e 3 | 3 min | 4 min |
| 3 | Objetivos | 4 | 2 min | 6 min |
| 4 | Fundamentação | 5 e 6 | 3 min | 9 min |
| 5 | Trabalhos relacionados e lacuna | 7 | 3 min | 12 min |
| 6 | Requisitos e pontos críticos | 8 e 9 | 3 min | 15 min |
| 7 | Como as explicações são geradas | 10 | 3 min | 18 min |
| 8 | Arquitetura e modelos | 11 e 12 | 3 min | 21 min |
| 9 | Demonstração | 13 | 6 min | 27 min |
| 10 | Resultados | 14 | 4 min | 31 min |
| 11 | Limitações | 15 | 2 min | 33 min |
| 12 | Trabalhos futuros | 16 | 1 min | 34 min |
| 13 | Conclusão | 17 | 1 min | 35 min |

**Se atrasar, corte nesta ordem:** o slide 6 (fique só com a frase-chave), os detalhes dos trabalhos relacionados (fique só com a lacuna) e o passo 4 da demonstração.

---

## 1. Abertura (1 min) · slide 1

**Mostrar:** título, seu nome, orientadora, UFV Campus Rio Paranaíba, 2026.

**Dizer:**
- "Bom dia (ou boa tarde). Meu nome é João Pedro, e vou apresentar o meu TCC, orientado pela professora Adriana Zanella Martinhago."
- "Em uma frase: desenvolvi uma ferramenta que explica código Python para programadores com deficiência visual, com um texto feito para ser ouvido, e entrega essa explicação pela voz do leitor de tela NVDA."

## 2. Problema e motivação (3 min) · slides 2 e 3

**Slide 2: como um programador cego lê código**
- O leitor de tela entrega a informação em sequência, pela fala. Montar de cabeça a organização de um programa só ouvindo é custoso. No texto, isso aparece como a premissa de projeto do trabalho.
- A literatura registra barreiras concretas:
  - Nascimento, Barbosa e Viana (2022): questionário com 10 desenvolvedores com deficiência visual. Eles relataram dificuldade para navegar entre os arquivos de um projeto, depurar e localizar erros de sintaxe.
  - Estudo de caso em uma disciplina de programação (SBSI 2020): o leitor de tela sozinho não transmite a estrutura do código, porque a indentação não é falada, e as mensagens de erro de compilação no painel da IDE não eram lidas.
  - Testes de ambientes de desenvolvimento web com o NVDA (REIC): erros de sintaxe não são anunciados, e a saída do terminal é inacessível ou só parcialmente acessível.

**Slide 3: e a Inteligência Artificial?**
- Santos e colegas (2025): quatro programadores totalmente cegos fizeram o mesmo exercício com e sem IA. A IA corrigiu erros em segundos e aumentou a produtividade e a confiança, mas as sugestões exibidas na tela não eram lidas pelo leitor de tela.
- **Frase-chave:** "O problema não é só gerar a explicação. É entregar a explicação de um jeito que dê para ouvir."

## 3. Objetivos (2 min) · slide 4

**Mostrar:** o objetivo geral e os sete específicos, agrupados.

**Dizer:**
- Objetivo geral: "Desenvolver e avaliar tecnicamente um protótipo que gera explicações estruturadas de código Python, com foco nos pontos críticos e na regra de negócio, e as entrega a programadores com deficiência visual pelo leitor de tela."
- Específicos, em uma linha cada: revisão da literatura; requisitos e critérios de pontos críticos; estrutura de explicação acessível; o protótipo; seleção e comparação de modelos; validação técnica com o NVDA e com as regras de acessibilidade; protocolo de avaliação com usuários.
- **Dica:** diga com clareza o que foi cumprido e o que não foi. A banca vai comparar esta lista com os resultados do bloco 10.

## 4. Fundamentação (3 min) · slides 5 e 6

**Slide 5: leitores de tela e o NVDA** (mostre a Figura 1)
- O NVDA é gratuito, de código aberto e roda no Windows. Foi o leitor de tela mais citado pelos respondentes de Nascimento, Barbosa e Viana (2022).
- Ele também recebe texto de outros programas pela biblioteca NVDA Controller Client, uma DLL do NV Access. É por ela que o protótipo fala o relatório.

**Slide 6: modelos de linguagem e engenharia de prompts**
- Arquitetura Transformer (Vaswani et al., 2017). Com mais escala, o modelo executa tarefas novas a partir de poucos exemplos ou de instruções (Brown et al., 2020). Mas a escala sozinha não faz o modelo seguir a intenção do usuário; o ajuste com retorno humano melhora isso e ainda deixa erros simples (Ouyang et al., 2022).
- Há modelos de pesos abertos que rodam no próprio computador, como Qwen3 e GPT-OSS, pelo Ollama. Atenção à janela de contexto: abaixo de 24 GiB de memória de vídeo, o Ollama usa cerca de 4 mil tokens por padrão, e o protótipo configura 8192.
- **Frase-chave:** "Para quem ouve, o prompt precisa controlar a forma do texto, e não só o conteúdo."

## 5. Trabalhos relacionados e lacuna (3 min) · slide 7

- **Santos e colegas (2025):** IA com programadores cegos. A forma de entregar a saída é uma barreira.
- **Jorge e colegas (WAE):** criação de páginas web acessíveis com Grid Coding e YAML. Na avaliação com o ASES, 8 dos 9 componentes atingiram 95%, e a saída não foi testada com usuários cegos.
- **Zen e Tavares (2025):** 21 diretrizes para IDEs em 8 categorias, entre elas compreensão do código e sobrecarga auditiva. A validação foi qualitativa.
- **Sun e colegas (2023):** o ChatGPT resumindo código ficou abaixo dos modelos de referência em BLEU e ROUGE-L, e essas métricas não dizem nada sobre a escuta.
- **Lacuna (frase-chave):** "Nenhum desses trabalhos junta as quatro coisas: explicar o código que já existe, apontar os pontos críticos, relacionar com a regra de negócio e entregar pelo leitor de tela."

## 6. Requisitos e pontos críticos (3 min) · slides 8 e 9

**Slide 8: requisitos**
- Funcionais: analisar o projeto inteiro e avisar dos erros de sintaxe; apontar pontos críticos por regras fixas e agrupá-los por região; gerar visão geral e explicação por região, com modelo local ou em nuvem; entregar em texto e pela fala do NVDA; analisar com um único comando, na pasta do projeto, com menu de pastas opcional.
- Não funcionais: texto para escuta; diferença audível entre fato e dedução; falhas ditas em palavras, nunca em silêncio; reprodutibilidade; possibilidade de execução local.

**Slide 9: os cinco tipos de ponto crítico** (mostre a tabela da Seção 4.2)

| Tipo | Gravidade |
|---|---|
| Chamada a dependência externa (arquivo, rede, banco) | 5 |
| Tratamento de exceção (`try`/`except`) | 4 |
| Condicionais aninhados em 3 ou mais níveis | 3 |
| Laços aninhados em 2 ou mais níveis | 3 |
| Valor fixo em condição (por exemplo, `idade >= 18`) | 2 |

- Dois filtros reduzem falsos positivos: verbos ambíguos como `get` e `save` só contam se o arquivo importa biblioteca de rede ou de banco, e valores triviais (0, 1, -1, None, True, False e texto vazio) não contam.
- Os pontos são agrupados pela função que os contém: quem ouve recebe primeiro quantos pontos a região tem e depois o detalhe de cada um.
- **Frase-chave:** "Quem decide o que é crítico não é o modelo. É a análise estática, sempre do mesmo jeito."

## 7. Como as explicações são geradas (3 min) · slide 10

- Duas modalidades: a visão geral do projeto, em até 8 frases, e uma explicação por região, em até 12.
- Cada pedido ao modelo leva as regras e os dados da análise: definições, pontos de entrada, dependências externas, quem chama a região, o que ela chama, os pontos críticos e o código com as linhas numeradas.
- Regras de conteúdo: usar só os dados enviados; dizer primeiro o que o trecho faz e depois por que cada ponto merece atenção; declarar o que não estiver disponível; começar toda dedução com a palavra **"Inferência:"**.
- Regras de forma: frases de até 20 palavras; sem tabelas, listas, títulos, negrito ou símbolos; o nome de cada função dito uma vez; marcas faladas como "Primeiro", "Em seguida" e "Por fim".
- Temperatura zero e semente fixa. Um prompt que não cabe no contexto é recusado, e não cortado em silêncio.
- **Frase-chave:** "Quem ouve não vê que uma frase é suposição. Precisa ouvir isso."

## 8. Arquitetura e modelos (3 min) · slides 11 e 12

**Slide 11: a Figura 2** (a legenda já informa que ela foi gerada com o auxílio de IA)
- Percorra o fluxo: projeto Python → Tree-sitter monta a árvore sintática e avisa dos erros de sintaxe → regras de pontos críticos e mapa do projeto (definições, importações, grafo de chamadas) → montagem dos prompts → modelo pelo Ollama, por uma interface única → texto impresso e fala pelo NVDA.
- Política de falhas: um erro de configuração (servidor fora do ar, modelo ausente) interrompe na hora; um erro isolado afeta só aquela região, que é declarada sem explicação, e não omitida. O NVDA é conferido antes da análise, para o erro aparecer em segundos.

**Slide 12: escolha dos modelos**
- Critérios: privacidade e execução local, caber em 16 GB de memória, português e código, janela de contexto, custo e reprodutibilidade.
- Candidatos: `qwen3:8b` (padrão), `qwen3:14b`, `gpt-oss:20b` e `gemma4:31b` na nuvem, só com código de exemplo.
- O GPT-4o e o Llama 3 da proposta saíram da implementação, e o texto justifica isso (Seção 4.5).

## 9. Demonstração (6 min) · slide 13 e terminal

**Antes da banca (na véspera):**
- No computador da apresentação, rode `powershell -ExecutionPolicy Bypass -File .\preparar_windows.ps1 -Falar` na pasta `prototipo`. O NVDA deve falar a frase de teste.
- Ainda na pasta `prototipo`, rode uma vez `powershell -ExecutionPolicy Bypass -File .\instalar_comando.ps1`, feche o terminal e abra outro. A partir daí o comando `analisar` funciona em qualquer pasta.
- Teste com o NVDA fechado: entre em `prototipo\testes\fixtures\projeto_exemplo` e rode `analisar --falar`. Ele deve abrir o NVDA sozinho, em até 20 segundos.
- Gere a explicação de reserva, para não depender de rede nem esperar o modelo. Na pasta `prototipo`: `analisar testes\fixtures\projeto_exemplo --explicar --saida saida_demo.txt`.
- Grave um vídeo curto da demonstração com o áudio do NVDA. Ele é o plano B.

**Ao vivo:**
1. **(1 min) Um comando, na pasta do projeto.** Abra um terminal novo. Se quiser mostrar o tratamento de erro, digite `analisar` ainda na pasta pessoal: a ferramenta não analisa nada e diz como seguir. Depois entre no projeto de exemplo, `cd Documents\TCC_ll\prototipo\testes\fixtures\projeto_exemplo`, e digite só `analisar --falar`. Se o NVDA estiver fechado, a ferramenta avisa e o abre sozinha; vale mostrar isso à banca. Diga que, sem caminho, a pasta atual é analisada, e que o menu de pastas continua como opção (`analisar --menu`), para quem prefere escolher a pasta sem digitar caminho.
2. **(2 min) Relatório falado.** O NVDA lê: 6 pontos críticos em 4 regiões; região 1 de 4, `salvar`, no arquivo `persistencia.py`, severidade máxima 5 (chamada ao banco e `try`/`except`). Aponte a posição dita em palavras ("região 1 de 4") e a ausência de tabelas. Interrompa a fala com Ctrl depois da primeira região.
3. **(2 min) Explicação do modelo.** Abra o `saida_demo.txt`, que ficou na pasta `prototipo`, ou deixe o NVDA ler um trecho. Aponte uma frase que comece com "Inferência:".
4. **(1 min, opcional) Arquivo com erro.** Sem sair da pasta, rode `analisar ..\projeto_quebrado` (o caminho também pode vir depois do comando). A ferramenta avisa do erro de sintaxe em vez de analisar um arquivo incompleto em silêncio.

**Plano B:** se o NVDA, o atalho ou o terminal falharem, passe o vídeo e mostre o texto do relatório num slide. Não dependa de internet na demonstração.

**Dicas:** fonte grande no terminal; voz do NVDA mais lenta para a banca acompanhar; som do computador na caixa da sala; NVDA em silêncio durante os slides (NVDA+S alterna o modo de fala), ligado só na demonstração.

## 10. Resultados (4 min) · slide 14

- **Testes automatizados:** 198 testes passam em Linux, sem modelo, rede, NVDA nem Windows (servidor do Ollama falso, DLL falsa, entradas e pastas simuladas). [Se você rodar no Windows antes da defesa: "198 aprovados no Windows em DD/MM".]
- **NVDA (18/10/2026, Windows):** a DLL de 64 bits carregou, a verificação respondeu com o NVDA aberto e o relatório foi falado, confirmado por escuta. [Acrescente o que registrar: versão do NVDA, chamadas seguidas, fala duplicada, Windows bloqueado.]
- **Execução na nuvem (`gemma4:31b`, projeto de exemplo):** visão geral e duas regiões em 3,06 s, valor registrado no `saida_gemma4.json`. Em três textos, o modelo manteve o "Inferência:", as frases de até 20 palavras e a ausência de símbolos. Mas deixou um sublinhado num nome de função e deu a uma gravidade uma justificativa que não estava nos dados.
- **Frase-chave:** "Funciona de ponta a ponta, e os dois defeitos mostram por que a análise estática continua sendo a fonte dos fatos."
- [Se a comparação entre modelos estiver pronta: conformidade às regras por modelo, cobertura dos pontos críticos, tempo de geração e o modelo recomendado.]
- [Se não estiver: "A comparação entre modelos e o verificador automático são a próxima etapa. Deles depende a escolha do modelo recomendado."]

## 11. Limitações (2 min) · slide 15

- A validação é técnica. Ela não mede compreensão: sem avaliação com usuários, o trabalho não pode afirmar que ajuda.
- O modelo pode afirmar sem respaldo. O "Inferência:" só marca o que o próprio modelo reconhece como dedução, e a verificação de forma não garante a verdade.
- Só Python; chamadas resolvidas pelo nome; lista fechada de cinco tipos.
- O modo em nuvem envia o código a terceiros, por isso só é usado com código de exemplo.
- A fala usa só o NVDA no Windows, não confere tela bloqueada e envia o relatório numa chamada só.
- O comando e o menu de pastas ainda não foram testados com o NVDA nem com pessoas cegas, e dependem de o leitor de tela ler o terminal.
- **Frase-chave:** "Deixar a limitação clara também é resultado."

## 12. Trabalhos futuros (1 min) · slide 16

- **Porte para macOS e Linux:** a análise, o menu e a geração já não dependem do Windows, e os testes já rodam em Linux. Falta a fala com os leitores de tela desses sistemas, pela interface de fala que já existe, um comando e uma instalação equivalentes e a validação em cada sistema.
- Avaliação com programadores com deficiência visual; nível de detalhe ajustável; navegação pelos resultados, região por região, com explicação sob demanda; outras linguagens; integração com IDEs.

## 13. Conclusão (1 min) · slide 17

- "Separar quem decide o que é crítico, que é a análise estática, de quem explica, que é o modelo com regras para a escuta, se mostrou tecnicamente viável."
- "O próximo passo, e o mais importante, é ouvir quem vai usar a ferramenta."
- "Obrigado. Fico à disposição para as perguntas."

---

## Checklist

- [ ] Ensaiar duas vezes com cronômetro. A meta é 35 minutos.
- [ ] Rodar o `preparar_windows.ps1 -Falar` no computador da apresentação.
- [ ] Rodar o `instalar_comando.ps1` e testar o `analisar --falar` dentro do projeto de exemplo, com o NVDA fechado (ele deve abrir o NVDA sozinho).
- [ ] Gerar o `saida_demo.txt` e gravar o vídeo de reserva.
- [ ] Conferir o som do NVDA na caixa da sala.
- [ ] Levar os slides em PDF num pendrive.
- [ ] Desligar notificações do computador.
- [ ] Ler as perguntas abaixo em voz alta.

---

## 7 perguntas que a banca pode fazer

**Como responder:** comece pela resposta curta e só detalhe se pedirem. Se não souber, diga o que sabe e o que fica como limitação ou trabalho futuro. Não invente número.

### 1. Por que usar análise estática para achar os pontos críticos, em vez de pedir tudo ao modelo?

**Resposta curta:** porque o que é crítico precisa ser decidido sempre do mesmo jeito. A análise estática é determinística: o mesmo código gera sempre os mesmos pontos, sem custo de modelo e sem risco de invenção. O modelo só redige a explicação a partir desses dados.

**Se pedirem mais:** isso também torna a explicação verificável, porque todo ponto enviado precisa aparecer no texto. E mantém a ferramenta útil quando o modelo falha: a análise estática é entregue mesmo sem o Ollama. O preço é a cobertura, porque a lista é fechada em cinco tipos e não cobre padrões de frameworks.

**No texto:** Seções 4.2 e 4.3; Capítulo 6.

### 2. Como você sabe que as explicações ajudam de fato um programador cego?

**Resposta curta:** ainda não sei, e o trabalho diz isso. A validação feita é técnica: mostra que o código é analisado, que o texto segue as regras e que o NVDA fala. Ela não mede compreensão.

**Se pedirem mais:** para medir, o trabalho propõe um protocolo. Os participantes respondem a perguntas sobre a finalidade do trecho, a regra de negócio e os pontos críticos, com e sem a explicação, e são registrados acertos, tempo e percepção. É inspirado em Santos e colegas (2025). Os estudos da área usam amostras pequenas (4 e 10 participantes), e a participação exige consentimento e os procedimentos de ética. [Se aplicar o protocolo: os resultados.] Se não for aplicado, essa é a principal limitação e o primeiro trabalho futuro.

**No texto:** Seção 4.6.5; Capítulo 6.

### 3. O que impede o modelo de inventar uma regra de negócio?

**Resposta curta:** três coisas. O prompt manda usar só os dados enviados e dizer o que não está disponível. Toda dedução começa com a palavra "Inferência:", para quem ouve separar fato de suposição. E o relatório termina avisando que o texto pode ter erros e deve ser conferido no código.

**Se pedirem mais:** isso reduz o risco, mas não elimina. Na execução exploratória, o modelo deu a uma gravidade uma justificativa que não estava nos dados. O verificador automático confere forma e cobertura, não a verdade; por isso o trabalho prevê revisão manual de uma amostra.

**No texto:** Seções 4.3, 4.6.3 e 5.1; Capítulo 6.

### 4. Por que esses modelos, e não o GPT-4o e o Llama 3 da proposta?

**Resposta curta:** a escolha passou a seguir critérios explícitos: privacidade e execução local, caber em 16 GB de memória, desempenho em português e em código, janela de contexto, custo e reprodutibilidade. O GPT-4o só é oferecido por API, o que manda o código para fora do computador e tem custo por requisição.

**Se pedirem mais:** os candidatos são o `qwen3:8b` (padrão, cerca de 5,2 GB e suporte a 119 idiomas), o `qwen3:14b`, o `gpt-oss:20b` (forte em código e mais fraco em tarefas multilíngues) e o `gemma4:31b` na nuvem, só com código de exemplo. O Llama 3 pode entrar na comparação, porque o cliente aceita qualquer modelo do Ollama. [O modelo recomendado: resultado da comparação.]

**No texto:** Seções 2.3.2 e 4.5.

### 5. Os estudos que você cita dizem que o terminal é pouco acessível. Por que uma ferramenta de terminal?

**Resposta curta:** é uma tensão real, e ela está nas limitações. O relatório não depende de o leitor de tela ler o terminal: com `--falar`, ele vai direto ao NVDA pela biblioteca do NV Access. E o uso cabe num comando: a pessoa entra na pasta com `cd`, como em qualquer terminal, e digita `analisar`; o menu opcional foi feito para ser lido linha a linha, sem redesenho de tela, cores ou teclas especiais.

**Se pedirem mais:** o comando e o menu ainda não foram testados com o NVDA real nem por pessoas cegas, e a integração com IDEs está nos trabalhos futuros. Um argumento seu, que não está no texto: o terminal permite usar a ferramenta só com o teclado, sem interface gráfica. Se perguntarem por que o menu virou opção: no seu próprio uso, abrir o menu toda vez se mostrou pouco prático; quem já está na pasta ou sabe o caminho só precisa do comando (Seção 4.4).

**No texto:** Seção 4.4; Capítulo 6.

### 6. Como os pontos críticos e as gravidades foram definidos? Não são arbitrários?

**Resposta curta:** são uma escolha de projeto, declarada e verificável. Os cinco tipos miram trechos que concentram risco ou regra de negócio, e a gravidade serve para ordenar a fala, do mais grave para o menos grave. Ela não é uma medida calibrada de risco.

**Se pedirem mais:** dependência externa vale 5; tratamento de exceção, 4; condicionais aninhados em três ou mais níveis e laços aninhados, 3; valor fixo em condição, como `idade >= 18`, vale 2. Os filtros existem porque, sem eles, a ferramenta errava: rodando o analisador sobre o próprio código, todo `dicionario.get` virava dependência externa de gravidade 5. Se insistirem, diga que calibrar as gravidades com usuários é um aprimoramento possível.

**No texto:** Seção 4.2 e tabela de critérios.

### 7. Como a IA foi usada na elaboração do trabalho, e como você garante que domina o que foi gerado?

**Resposta curta:** aponte a Seção 4.7, que declara os usos conforme as diretrizes da UFV: a Figura 2, a revisão bibliográfica, a revisão gramatical, o código e rascunhos de seções. Depois explique, com suas palavras, como foi a divisão do trabalho: o que você definiu, o que conferiu e o que testou.

**Se pedirem mais:** a banca pode perguntar qualquer coisa sobre o trabalho (Regulamento, Art. 27). Esteja pronto para explicar qualquer arquivo do protótipo e qualquer seção do texto, e para mostrar de qual registro vem cada número.

**No texto:** Seção 4.7.
