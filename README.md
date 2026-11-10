# Tutor multiagente de Strategy e Adapter

Trabalho de ELC1070, Análise e Projeto de Sistemas OO.

O sistema ensina dois padrões de projeto usando CrewAI e o modelo `qwen2.5:7b` no
Ollama. Roda inteiro na máquina local, sem API paga, chave ou internet durante a
execução.

## O que ele faz

O tutor identifica a intenção da mensagem e injeta no prompt apenas os fatos do tópico
pedido. As respostas são curtas, com uma pergunta ao final para manter o aluno
raciocinando.

- **contexto, problema, conceito, participantes, mecanismo, custos, quando,
  confusões, erro e fechamento:** explicações ancoradas no conteúdo verificado.
  No primeiro contato o tutor começa pelo `contexto` (o que é um padrão de projeto,
  o catálogo GoF e a categoria); nas mensagens seguintes avança para `conceito`.
- **exemplo:** um programa Java fixo e verificado é exibido; o modelo só comenta o
  código, sem reescrevê-lo.
- **exercício:** cenário, tarefa, critérios e perguntas de partida, sem solução.
- **avaliação:** feedback sobre a tentativa do aluno, com um conceito a revisar.
- **comparação:** contraste direto entre Strategy e Adapter.
- **conversa:** saudações, mensagens vagas e padrões fora do escopo passam pelo
  modelo para uma resposta curta e natural; se ele falhar, entra uma mensagem fixa.
- **recusas:** pedidos para inventar um padrão ou entregar a solução pronta são
  recusados sem chamar o modelo.

Cinco papéis: roteador, tutor, exemplificador, inquiridor e guardião. O roteador só
entra quando as regras determinísticas não conseguem classificar a mensagem. O
guardião revisa o texto e pode pedir uma correção; se as duas tentativas falharem,
entra um fallback montado só com os fatos verificados.

## Arquivos principais

```
agente/
  conhecimento.py     # fatos por tópico, pedagogia e exercícios fixos
  roteador.py         # intenção por regras; LLM só quando ambíguo
  estado.py           # tópicos vistos, dificuldades, exercício pendente
  prompts.py          # agentes, regras e tarefas
  validadores.py      # checagens determinísticas
  motor.py            # único ponto que usa CrewAI/Ollama
  tutor.py            # orquestra roteia -> produz -> valida -> regenera -> fallback
  chat.py             # interface Gradio opcional
  __main__.py         # CLI
testes/test_tutor.py  # testes sem modelo
docs/                 # prompts, justificativa, relatório e caderno
evidencias/           # cenários e pareceres registrados
```

## Instalação

```powershell
cd qwen_stg
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull qwen2.5:7b
```

O `.env` desliga tracing e telemetria do CrewAI. O CrewAI e o LiteLLM carregam esse
arquivo sozinhos. O Gradio é opcional; instale com
`.\.venv\Scripts\python.exe -m pip install gradio` se quiser a interface web.

## Como rodar

```powershell
# uma pergunta e sai
.\.venv\Scripts\python.exe -m agente "Explique o padrão Strategy."

# conversa com memória
.\.venv\Scripts\python.exe -m agente

# interface web, se o gradio estiver instalado
.\.venv\Scripts\python.exe -m agente --chat
```


Algumas perguntas para testar:

```text
Explique o padrão Adapter e para que serve.
Qual a diferença entre Strategy e State?
Me dê um exercício sobre Adapter.
Como o Adapter costuma ser aplicado de forma errada?
O que devo lembrar antes de usar Strategy?
Minha resposta: ...
```

## Decisões antes de chamar o modelo

| Situação | Como o sistema reconhece | O que acontece |
|---|---|---|
| Pergunta sobre um padrão | `strategy`/`estratégia` ou `adapter`/`adaptador` | intenção por palavra-chave |
| Pedido de prática | "exercício", "praticar", "desafio", "testar" | modo exercício |
| Tentativa de resposta | "Minha resposta:" ou fala com sinal de resposta | modo avaliação |
| Abandono do exercício | "outro tópico", "pular", "deixa pra lá" | limpa o exercício pendente |
| Saudação ou conversa | "oi", "olá", mensagem vaga | resposta curta pelo modelo |
| Pergunta ambígua | cita os dois padrões | comparação |
| Padrão fora do escopo | cita outro padrão GoF | recusa com honestidade |
| "Invente um padrão" | "invente", "padrão fictício", entre outras | recusa |
| "Me dê a solução pronta" | "solução completa", "resolva para mim", entre outras | recusa |

A pergunta atual tem prioridade sobre o histórico. Só quando ela não cita um padrão o
sistema usa o padrão em estudo.

## Fluxo

```
mensagem
   ├─ rotear()                  regras em Python; LLM só se ambíguo
   ├─ recusa determinística?    invenção, solução pronta, fora do escopo
   ├─ produção                  tutor/exemplificador/inquiridor + guardião
   ├─ validação                 regras determinísticas
   ├─ regeneração               1 nova tentativa com correção obrigatória
   ├─ fallback                  texto montado só com fatos verificados
   └─ registro                  evidencias/execucoes.jsonl
```

Pontos que valem saber:

- Um único objeto `LLM` é criado e reutilizado em todas as chamadas.
- `allow_delegation=False` evita chamadas extras decididas pelo modelo.
- O conteúdo entra no prompt por tópico, não inteiro.
- O exemplo Java e os exercícios fixos são verificados e não dependem do modelo.
- O histórico é curto e truncado por mensagem.
- O parecer do guardião não aparece no chat; vai para o JSONL de evidências.

## Testes

Os testes não chamam o modelo e rodam em menos de um segundo:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s testes -v
```

São 52 testes. Um deles só roda se houver `javac` no ambiente; os outros cobrem
roteamento, recusas, conversa, validação, fallback, estado do aluno, exercício e
avaliação.

## Limitações

- Modelo 7B local: a qualidade varia e às vezes a resposta fica repetitiva.
- `num_ctx=8192` é repassado ao Ollama via LiteLLM. Se não valer, crie um Modelfile
  com `PARAMETER num_ctx 8192`.
- O guardião também é um 7B. Por isso existem validadores determinísticos e fallback.
- O Gradio é opcional e não entra na instalação padrão.
- Os cenários de evidência precisam ser reexecutados depois de mudanças de prompt.

## Documentação

- `docs/PROMPTS.md`: prompts de cada agente e tarefa, gerado de `agente/prompts.py`.
- `docs/JUSTIFICATIVA.md`: por que o projeto ficou assim.
- `docs/MINI_RELATORIO.md`: ambiente, decisões e evidências.
- `docs/CADERNO_EVIDENCIAS.md`: cenários, respostas e análise.
- `COMO_TESTAR.md`: checklist e roteiro dos cenários.
