# Justificativa das decisões de projeto

Trabalho de ELC1070, Análise e Projeto de Sistemas OO.

## 1. Problema e recorte

O sistema ensina Strategy e Adapter a um estudante que ainda não domina esses
padrões. A restrição principal é de infraestrutura: tudo precisa rodar na máquina
local, sem API paga, chave, nuvem ou internet durante a execução.

Escolhi dois padrões em vez de muitos. Dois padrões bem cobertos rendem mais do que
vários vistos por cima. O recorte também permite comparar Strategy e Adapter, que é
uma confusão comum: o primeiro escolhe entre algoritmos com a mesma interface; o
segundo traduz uma interface existente para outra.

## 2. Cinco papéis, quatro funções pedagógicas

O tutorial da disciplina traz uma crew de três agentes (tutor, exemplificador e
avaliador) para SOLID. Esse formato não separa a função de exercitar e diagnosticar:
o avaliador revisa uma resposta, mas não conduz a prática.

O sistema usa quatro papéis pedagógicos e um de infraestrutura:

| Agente | Função | Responsabilidade |
|---|---|---|
| Tutor | ensinar | explicação curta, ancorada nos fatos do tópico |
| Exemplificador | exemplificar | comenta um programa Java já verificado |
| Inquiridor | exercitar e diagnosticar | exercício sem solução e feedback sobre a tentativa |
| Guardião | garantir confiabilidade | parecer interno sobre correção, invenção e lacunas |
| Roteador | classificar | intenção da mensagem, só quando as regras não bastam |

O roteador não é um agente pedagógico. Ele existe como rede de segurança para
mensagens ambíguas; na maioria dos turnos, a classificação acontece em Python.

## 3. Roteamento determinístico primeiro

A maior mudança em relação à primeira versão foi separar intenção de padrão. O
sistema classifica a mensagem em uma destas intenções: contexto, problema, conceito,
participantes, mecanismo, custos, quando, confusões, erro, fechamento, exemplo,
comparação, exercício, avaliação, abandono de exercício, continuação, dúvida e
conversa. No primeiro contato com um padrão, o pedido de explicação vira `contexto`
antes de `conceito`, para situar o aluno no catálogo GoF e na categoria do padrão.
Saudações, mensagens vagas e padrões fora do escopo passam pelo modelo em modo de
conversa, com mensagem fixa como reserva.

As regras rodam nesta ordem:

1. recusas de invenção e de solução pronta;
2. abandono de exercício pendente;
3. tentativa de resposta ao exercício;
4. saudação;
5. padrão citado na mensagem ou padrão em estudo;
6. padrão GoF fora do escopo;
7. pedido de exercício;
8. continuação da progressão;
9. pontuação por palavras-chave;
10. agente Roteador, apenas se nada casou.

Isso reduz latência e deixa as decisões auditáveis. O LLM só é consultado quando a
mensagem não tem sinal claro, e sua resposta é validada contra a lista de intenções.

## 4. Conteúdo verificado por tópico

O núcleo anti-alucinação é um objeto `Padrao` imutável, em Python, com definição,
intenção, problema, participantes, mecanismo, consequências, quando usar, quando
evitar, confusões, sinal prático, erro comum, analogia, pedagogia, progressão,
perguntas, exemplo Java, UML, exercício fixo e termos proibidos.

Cada intenção recebe apenas os tópicos de que precisa. Uma pergunta sobre custos não
leva o exemplo Java nem o UML; uma comparação leva os dois padrões e o contraste. Isso
diminui o contexto, reduz distração do modelo e evita que ele misture assuntos.

O exemplo Java de Strategy usa navegação (`RotaStrategy`, `Navegador`). O de Adapter
usa duas bibliotecas de pagamento fictícias com unidades e tipos de retorno
diferentes (`CartaoAdapter`, `PixAdapter`). O código é fixo e verificado; o modelo só
comenta, não reescreve. Essa foi a forma mais confiável de garantir que o exemplo
exibido implemente de fato o padrão.

## 5. CrewAI e Ollama

O enunciado pede um framework multiagente. Escolhi CrewAI porque declara agentes,
tarefas e fluxo em poucas linhas e já tem integração com o Ollama via LiteLLM. O
modelo é o `qwen2.5:7b`, quantizado em Q4_K_M, rodando na GPU local.

Um único objeto `LLM` é criado e reutilizado. Todos os agentes dividem as mesmas
configurações: temperatura 0,3, teto de 1.200 tokens de saída, timeout de 300 s e
contexto de 8.192 tokens.

`allow_delegation=False` em todos. Sem isso, o modelo pode tentar delegar uma
subtarefa e gastar chamadas extras. O fluxo já está definido pelas tarefas.

Não usei `memory=True`. A memória do CrewAI depende de embeddings e, na configuração
padrão, de uma API OpenAI, o que quebraria a restrição de custo zero. A memória é
estruturada em Python: padrão em estudo, tópicos vistos, dificuldades, exercício
pendente, tentativas e acertos, mais um histórico curto da conversa.

## 6. Três camadas de confiabilidade

A resposta não é o `raw` do modelo. Cada etapa tem uma barreira:

1. **Validação determinística.** Blocos de código são bloqueados onde não cabem;
   limite de palavras; termos incompatíveis com o padrão; exercício precisa ter as
   seções e não pode revelar o nome do padrão nem termos como Context, Target ou
   Adaptee; feedback precisa da pergunta de avançar e das linhas `RESULTADO` e
   `CONCEITO`.
2. **Guardião.** Outro agente revisa o texto contra os fatos e termina em
   `VEREDITO: OK` ou `VEREDITO: CORRIGIR`. Em caso de correção, o produtor tenta mais
   uma vez com a correção obrigatória.
3. **Fallback verificado.** Se as duas tentativas falharem, o sistema monta a resposta
   só com o conteúdo verificado. No exercício, usa o exercício fixo; na avaliação, um
   feedback fixo que não inventa julgamento.

O parecer do guardião não aparece no chat. Ele vai para `evidencias/execucoes.jsonl`,
junto com intenção, padrão, pergunta, tempo, tentativas e indicação de fallback.

## 7. Exemplo, exercício e diagnóstico

O exemplificador recebe o código pronto e é instruído a não reescrevê-lo nem inventar
classes. A resposta visível monta o código, a estrutura UML e dois blocos curtos: "O
que observar" e "Se amanhã...".

O inquiridor propõe exercícios sem código e sem solução. O cenário é diferente do
exemplo da aula e os nomes de classes não aparecem. Se o modelo vazar um termo
proibido, o validador rejeita e o exercício fixo entra no lugar.

Na avaliação, o inquiridor lê a tentativa, aponta o que está certo e o que falta, e
devolve um conceito para revisar. As linhas `RESULTADO` e `CONCEITO` são extraídas em
Python. Só `CORRETO` fecha o exercício; `PARCIAL` e `INCORRETO` mantêm o exercício
pendente e registram a dificuldade. O aluno pode pedir outro tópico para abandonar o
exercício; isso limpa o estado sem chamar o modelo.

## 8. Erros e confiabilidade

Além do guardião, existem barreiras determinísticas:

- pedido para inventar um padrão recebe recusa explícita, sem modelo;
- pedido de solução pronta recebe recusa pedagógica, sem modelo;
- padrão GoF fora do escopo é recusado com honestidade;
- fala longa sem sinal de resposta não é confundida com tentativa de exercício;
- falha do Ollama vira mensagem clara no CLI, sem traceback;
- 52 testes cobrem roteamento, validação, conversa, fallback, estado e fluxo.

## 9. Limitações

- O 7B leva de dezenas de segundos a mais de um minuto por resposta nesta máquina.
- `num_ctx=8192` é repassado via LiteLLM; se o Ollama ignorar, é preciso um Modelfile.
- O guardião também é um 7B e pode errar para mais e para menos. Por isso ele não é a
  única barreira.
- O Java é verificado e há teste de compilação quando `javac` está instalado; no
  ambiente principal não há JDK.
- O Gradio é opcional e ficou fora da instalação padrão.

## 10. Trabalhos futuros

- Validar o Java com um parser ou compilador em integração contínua.
- Usar embeddings locais, por exemplo via Ollama, para buscar material da disciplina
  sem API.
- Ampliar o catálogo mantendo o contrato `Padrao`.
- Testar com estudantes e comparar a profundidade percebida antes e depois das
  mudanças de prompt.
