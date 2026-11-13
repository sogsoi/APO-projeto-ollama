# Mini-relatório do processo

## Objetivo e ambiente

O objetivo era montar um sistema multiagente com CrewAI que ensinasse Strategy e
Adapter usando só um modelo local. Nada de API paga, chave, nuvem ou internet durante
a execução.

| Item | Configuração |
|---|---|
| CPU | Intel Core i5-6400 (4 núcleos, 2,7 GHz) |
| RAM | 16 GB |
| GPU | NVIDIA GeForce GTX 1070 (8 GB VRAM) |
| Sistema | Windows 11 |
| Python | 3.13.16 em `.venv` |
| CrewAI | 1.15.35 |
| Modelo | `qwen2.5:7b` (Q4_K_M, 4,7 GB) |
| Ollama | 0.40.14, backend Vulkan, contexto 8192 |

## Troca do CUDA pelo Vulkan

A primeira tentativa de usar a GPU falhou com `CUDA error: the provided PTX was
compiled with an unsupported toolchain`. A placa é compute capability 6.1 e o driver
instalado (560.94) é anterior ao 570 que o Ollama pede para essa faixa.

Desliguei o CUDA e usei o backend Vulkan, com `CUDA_VISIBLE_DEVICES=-1` e
`OLLAMA_VULKAN=1`. Ficou 100% GPU, contexto 8192 e cerca de 23 a 57 tokens/s. Com
driver 570 ou mais novo, dá para remover o desvio.

## O que mudou ao longo do caminho

**Três agentes viraram quatro funções pedagógicas.** O tutorial usa tutor,
exemplificador e avaliador. O Anexo A pede quatro funções: ensinar, exemplificar,
exercitar/diagnosticar e garantir confiabilidade. Separei um agente para cada uma e
deixei o roteador como apoio de classificação.

**O modo único virou intenção.** A primeira versão tinha três modos (aula, exercício e
avaliação) e uma mini-aula fixa de seis seções. A versão atual classifica a intenção
(contexto, problema, conceito, participantes, mecanismo, custos, quando, confusões,
erro, fechamento, exemplo, comparação, exercício, avaliação, abandono, continuação,
dúvida e conversa) e injeta apenas os fatos do tópico. A resposta fica curta e foca no
que o aluno perguntou. No primeiro contato, a explicação começa pelo `contexto`
(catálogo GoF e categoria) e só depois avança para `conceito` e `problema`.

**O exemplo deixou de ser gerado pelo modelo.** Antes, o exemplificador escrevia um
programa Java e o guardião revisava. O 7B às vezes inventava classes e misturava
domínios. Agora o exemplo é fixo e verificado; o modelo só comenta o código. A mesma
ideia vale para o exercício: se o modelo vazar o nome do padrão, entra o exercício
fixo.

**As respostas passaram a ter fallback determinístico.** Cada produção é validada por
regras e pelo guardião. Se as duas tentativas falharem, o sistema monta a resposta só
com os fatos verificados. Isso dá um piso de qualidade mesmo quando o modelo falha.

**O estado do aluno ficou explícito.** Em vez de passar só o texto da conversa, o
sistema guarda padrão em estudo, tópicos vistos, dificuldades, exercício pendente,
tentativas e acertos. O estado alimenta o resumo enviado ao modelo e permite retomar a
progressão.

**O roteador virou determinístico.** Palavras-chave resolvem a maioria dos casos. O
agente Roteador só é chamado quando nada casa, e sua resposta ainda é validada contra
a lista de intenções.

**Os testes ficaram executáveis sem CrewAI.** O import do CrewAI é tardio, dentro do
motor. Os testes usam um motor falso e cobrem roteamento, recusas, validação,
fallback, exercício, avaliação, conversa e estado. São 52 testes; o de compilação Java só roda
se houver `javac`.

**Os testes acharam furos.** O feedback podia ser aprovado sem as linhas
`RESULTADO`/`CONCEITO`, e o exercício nunca fechava. Uma fala longa sem pergunta podia
ser confundida com resposta ao exercício. "Não invente" era tratado como pedido de
invenção. Os três casos foram corrigidos e têm teste.

## Evidências da primeira versão

A tabela abaixo é da arquitetura antiga (três modos, mini-aula de seis seções). Fica
como histórico; os tempos e formatos não valem para a versão atual.

| Data/hora | Padrão | Modo | Tempo | Palavras | Parecer do guardião |
|---|---|---|---|---|---|
| 05/11 16:29 | Strategy | aula | 107,7 s | 904 | CORRIGIR, mistura de frete com navegação |
| 05/11 16:33 | Strategy | aula | 110,5 s | 1.278 | OK, não viu a repetição do problema |
| 05/11 16:36 | Strategy | aula | 90,1 s | 1.198 | CORRIGIR, falso positivo no if/else didático |
| 05/11 16:39 | Adapter | aula | 98,8 s | 1.002 | OK, não viu o teste confuso com Bridge |

Os registros completos daquela versão estão em `evidencias/execucoes.jsonl`. A versão
atual grava os mesmos campos, com `intencao` no lugar de `modo`.

## O que funcionou

- O conteúdo verificado no prompt impediu participantes e consequências inventados.
- O exemplo Java fixo eliminou classes inventadas.
- Os validadores e o fallback deram piso de qualidade nos casos em que o 7B falhou.
- A resposta curta com pergunta final combina com o formato de conversa.
- "Invente um padrão", "me dê a solução pronta" e padrões fora do escopo são recusados
  sem gastar modelo.
- Os testes rodam sem CrewAI e sem rede.

## O que ainda limita

- O 7B varia entre execuções e às vezes repete trechos.
- O guardião pode errar para os dois lados.
- `num_ctx=8192` depende do repasse pelo LiteLLM.
- Sem `javac` no ambiente principal, a compilação do Java não é testada aqui.
- Os cenários de evidência precisam ser reexecutados com a nova arquitetura.

## Próximos passos

Rodar o roteiro de `COMO_TESTAR.md` com a versão atual, preencher o caderno de
evidências, comparar os tempos por intenção e revisar a documentação final.
