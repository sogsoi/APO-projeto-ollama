# Como testar

Rode tudo na pasta `qwen_stg`, chamando o Python do venv. Não precisa ativar o
ambiente:

```powershell
cd C:\Users\ratoyy\qwen_stg
```

## 1. Ambiente

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -c "import crewai; print(crewai.__version__)"
```

Esperado: Python 3.13.x e CrewAI 1.15.x.

## 2. Ollama

```powershell
curl http://localhost:11434
ollama list
ollama ps
```

O `curl` deve responder `Ollama is running`. O `ollama list` deve mostrar o
`qwen2.5:7b` e o `ollama ps` deve indicar `100% GPU` na coluna PROCESSOR. Se
aparecer erro de PTX/CUDA, o backend Vulkan não está ativo.

## 3. Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s testes -v
```

Esperado: 52 testes. Um é pulado se não houver `javac`; os demais devem passar.

## 4. Uma pergunta pela CLI

```powershell
.\.venv\Scripts\python.exe -m agente "Explique o padrão Strategy e qual problema ele resolve."
```

A resposta deve ser curta, em tom de conversa, e terminar com uma pergunta. O tempo
aparece no `stderr` como `(tempo: Ns)`.

## 5. Conversa com memória

```powershell
.\.venv\Scripts\python.exe -m agente
```

```text
Você: explique o padrão Adapter
Você: e quando evitar?
Você: sair
```

A segunda pergunta deve continuar no contexto do Adapter, sem pedir o nome do padrão
de novo.

## 6. Exercício e avaliação

```powershell
.\.venv\Scripts\python.exe -m agente
```

```text
Você: me dê um exercício sobre Strategy
Você: Minha resposta: usaria uma interface comum para o cálculo, com implementações separadas, e o contexto receberia a regra pronta e poderia trocá-la.
Você: quero outro tópico
Você: sair
```

No exercício devem aparecer cenário, tarefa, critérios, perguntas de partida e a
instrução "Responda começando por **Minha resposta:**". Nada de código ou solução.

Na avaliação devem aparecer o que está correto, o que está incompleto, o conceito a
revisar e uma pergunta para avançar. As linhas `RESULTADO:` e `CONCEITO:` são
removidas da resposta visível.

O pedido "quero outro tópico" deve limpar o exercício pendente e retomar a conversa
sem chamar o modelo.

## 7. Exemplo em Java

```powershell
.\.venv\Scripts\python.exe -m agente "Dê um exemplo de Adapter em Java"
```

O código exibido é o exemplo verificado (`class PixAdapter`, `class CartaoAdapter`). O
modelo comenta o código; ele não reescreve o programa.

## 8. Recusas sem modelo

```powershell
.\.venv\Scripts\python.exe -m agente "Invente um padrão chamado Z e explique para mim"
.\.venv\Scripts\python.exe -m agente "Me entregue o código pronto de uma solução completa"
```

As duas respostas devem sair em menos de um segundo, com recusa educada e sem
chamada ao modelo.

Padrões fora do escopo passam pela conversa e usam o modelo:

```powershell
.\.venv\Scripts\python.exe -m agente "Explique o Observer"
```

A resposta deve dizer com honestidade que o Observer não faz parte do material e
oferecer Strategy ou Adapter, sem explicar o Observer.

## 9. Modelo fora do ar

Pare o Ollama e rode:

```powershell
.\.venv\Scripts\python.exe -m agente "Explique o padrão Strategy"
```

Deve aparecer uma mensagem pedindo para verificar o Ollama, sem traceback.

## 10. Sem internet

Desligue o Wi-Fi e repita o teste 4. A resposta deve continuar funcionando.

## Roteiro dos cenários

Rode cada pergunta para Strategy e para Adapter. Anote a resposta, a correção e a
utilidade pedagógica.

| # | Categoria | Pergunta | Intenção esperada |
|---|---|---|---|
| 1 | Conceitual | "Explique o padrão X e qual problema ele resolve." | contexto (primeiro contato) |
| 2 | Exemplo | "Dê um exemplo de aplicação do padrão X em Java." | exemplo |
| 3 | Seleção | "Descreva uma situação em que X é a melhor escolha e uma em que ele deve ser evitado." | quando |
| 4 | Uso incorreto | "Como X costuma ser aplicado de forma errada? Como corrigir?" | erro |
| 5 | Conceito equivocado | "Com qual padrão X é mais confundido? Qual a diferença?" | confusoes |
| 6a | Anti-alucinação | "Invente um padrão chamado Z e explique." | recusa determinística |
| 6b | Anti-alucinação | "Me entregue o código pronto de uma solução completa." | recusa determinística |
| 7 | Fechamento | "O que devo lembrar antes de usar X?" | fechamento |
| 8 | Exercício | "Me dê um exercício sobre X." | exercício |
| 9 | Diagnóstico | "Minha resposta: ..." (depois do exercício) | avaliação |
| 10 | Comparação | "Qual a diferença entre Strategy e Adapter?" | comparar |

Para rodar os cenários 1 a 8 de uma vez:

```powershell
.\.venv\Scripts\python.exe docs\rodar_cenarios.py
```

As saídas ficam em `evidencias/cenarios/`, com um `.txt` e um `.err` por cenário. Os
tempos e pareceres vão para `evidencias/execucoes.jsonl`. O script pula cenários que
já têm saída, então pode ser retomado.

Para o par exercício e avaliação, que precisa de memória entre turnos:

```powershell
.\.venv\Scripts\python.exe docs\rodar_avaliacoes.py
```

Para resumir as saídas e conferir tamanho, blocos Java e vazamento do nome do padrão:

```powershell
.\.venv\Scripts\python.exe docs\resumir_cenarios.py
```

## O que registrar

- data e hora do teste;
- a pergunta exata;
- um trecho da resposta;
- correção (correta, parcial ou incorreta), com justificativa;
- utilidade pedagógica (alta, média ou baixa);
- tempo de resposta, que a CLI imprime no `stderr`;
- parecer do guardião, em `evidencias/execucoes.jsonl`.

O `execucoes.jsonl` guarda sozinho data/hora, intenção, padrão, pergunta, tempo, modelo
e parecer.
