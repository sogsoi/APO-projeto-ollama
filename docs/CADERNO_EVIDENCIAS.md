# Caderno de evidências

Trabalho de ELC1070, Análise e Projeto de Sistemas OO.
Sistema: tutor multiagente de Strategy e Adapter (CrewAI + Ollama).

> **Nota sobre as versões.** A seção 4 reúne resultados da primeira versão do
> sistema, que tinha três modos e uma mini-aula de seis seções. A versão atual usa
> intenções, fatos por tópico e fallback determinístico. Os números antigos ficam como
> histórico; o roteiro da seção 3 precisa ser reexecutado para preencher a tabela da
> versão atual.

## 1. Ambiente

| Item | Configuração |
|---|---|
| CPU | Intel Core i5-6400 (4 núcleos, 2,7 GHz) |
| RAM | 16 GB |
| GPU | NVIDIA GeForce GTX 1070 (8 GB VRAM) |
| Sistema | Windows 11 |
| Python | 3.13.16 em `.venv` |
| CrewAI | 1.15.35 |
| Modelo | `qwen2.5:7b` Q4_K_M |
| Inferência | Ollama 0.40.14, 100% GPU, contexto 8192 |

## 2. Método

Rodei cada cenário pela CLI, num processo novo e sem histórico. A exceção é o par
exercício e avaliação, que usa o modo de conversa para manter o contexto.

```powershell
.\.venv\Scripts\python.exe -m agente "pergunta do cenário"
```

No par exercício e avaliação:

```powershell
.\.venv\Scripts\python.exe -m agente
```

O sistema grava três coisas:

- a resposta visível em `evidencias/cenarios/<cenário>.txt`;
- o tempo e o progresso em `evidencias/cenarios/<cenário>.err`;
- a decisão e o parecer do guardião em `evidencias/execucoes.jsonl`.

O JSONL da versão atual tem os campos `data_hora`, `intencao`, `motivo_rota`,
`padrao`, `pergunta`, `duracao_s`, `modelo`, `tentativas`, `parecer`, `problemas` e
`fallback`, quando existirem.

A avaliação qualitativa usa três critérios: correção em relação ao conteúdo
verificado, aderência à pergunta e utilidade pedagógica.

## 3. Roteiro da versão atual

| # | Cenário | Pergunta | Intenção esperada | Status |
|---|---|---|---|---|
| 1 | Conceito | "Explique o padrão X e qual problema ele resolve." | conceito | pendente |
| 2 | Exemplo | "Dê um exemplo de aplicação do padrão X em Java." | exemplo | pendente |
| 3 | Seleção | "Descreva uma situação em que X é a melhor escolha e uma em que ele deve ser evitado." | quando | pendente |
| 4 | Uso incorreto | "Como X costuma ser aplicado de forma errada? Como corrigir?" | erro | pendente |
| 5 | Confusão | "Com qual padrão X é mais confundido? Qual a diferença?" | confusoes | pendente |
| 6a | Anti-alucinação | "Invente um padrão chamado Z e explique." | recusa | pendente |
| 6b | Anti-alucinação | "Me entregue o código pronto de uma solução completa." | recusa | pendente |
| 6c | Fora do escopo | "Explique o Observer." | recusa | pendente |
| 7 | Fechamento | "O que devo lembrar antes de usar X?" | fechamento | pendente |
| 8 | Exercício | "Me dê um exercício sobre X." | exercício | pendente |
| 9 | Diagnóstico | "Minha resposta: ..." (depois do exercício) | avaliação | pendente |
| 10 | Comparação | "Qual a diferença entre Strategy e Adapter?" | comparar | pendente |
| 11 | Abandono | "Quero outro tópico" (com exercício pendente) | sem modelo | pendente |

Para a versão atual, registre também:

- se a resposta respeitou o limite de palavras da intenção;
- se o exemplo Java exibido é o verificado;
- se o exercício ficou sem o nome do padrão e sem código;
- se o feedback trouxe `RESULTADO` e `CONCEITO` no texto bruto e se essas linhas foram
  removidas da resposta visível;
- se houve regeneração (`tentativas: 2`) ou fallback (`fallback: true`).

## 4. Resultados da primeira versão

### 4.1 Cenários executados

Os tempos vêm da CLI (`(tempo: Ns)` no `stderr`) e não incluem o carregamento do
modelo. As respostas completas estão em `evidencias/cenarios/`.

| # | Cenário | Padrão | Tempo | Palavras | Formato | Parecer |
|---|---|---|---|---|---|---|
| 1 | `s1_conceito_strategy` | Strategy | 87 s | 1.142 | 6 seções + Java | OK |
| 1 | `s1_conceito_adapter` | Adapter | 95 s | 937 | 6 seções + Java | OK |
| 2 | `s2_exemplo_strategy` | Strategy | 84 s | 1.093 | 6 seções + 2 blocos Java | OK |
| 2 | `s2_exemplo_adapter` | Adapter | 81 s | 1.052 | 6 seções + Java | OK |
| 3 | `s3_selecao_strategy` | Strategy | 86 s | 1.100 | 6 seções + Java | OK |
| 3 | `s3_selecao_adapter` | Adapter | 85 s | 1.047 | 6 seções + Java | OK |
| 4 | `s4_uso_incorreto_strategy` | Strategy | 80 s | 986 | 6 seções + Java | OK |
| 4 | `s4_uso_incorreto_adapter` | Adapter | 72 s | 881 | 6 seções + Java | OK |
| 5 | `s5_confusao_strategy` | Strategy | 79 s | 1.015 | 6 seções + Java | OK |
| 5 | `s5_confusao_adapter` | Adapter | 82 s | 1.103 | 6 seções + Java | OK |
| 6a | `s6a_invencao` | — | < 1 s | 37 | recusa determinística | sem modelo |
| 6b | `s6b_solucao_pronta` | — | < 1 s | 33 | recusa determinística | sem modelo |
| 7 | `s7_fechamento_strategy` | Strategy | 77 s | 1.033 | 6 seções + Java | OK |
| 7 | `s7_fechamento_adapter` | Adapter | 141 s | 1.016 | 6 seções + Java | OK |
| 8 | `s8_exercicio_strategy` | Strategy | 19 s | 186 | cenário + tarefa + critérios | OK |
| 8 | `s8_exercicio_adapter` | Adapter | 18 s | 182 | cenário + tarefa + critérios | OK |
| 9 | `s9_avaliacao_strategy` | Strategy | 40 s | 150 | 4 blocos de feedback | OK |
| 9 | `s9_avaliacao_adapter` | Adapter | 38 s | 135 | 4 blocos de feedback | OK |

O cenário 9 é uma sessão de dois turnos, exercício e tentativa, e o tempo inclui os
dois. Os cenários 1 a 7 usavam três agentes; 8 e 9 usavam dois. Nenhuma execução
passou de 141 s.

### 4.2 Correção conceitual

As 14 aulas (cenários 1 a 7, dois padrões) seguiam o conteúdo verificado sem
contradição. Participantes e responsabilidades apareciam corretos. Strategy trazia
Context, Strategy, ConcreteStrategy e Cliente. Adapter trazia Target, Cliente, Adaptee
e Adapter. Nenhuma aula inventou participante, API ou biblioteca.

As duas aulas de confusão (cenário 5) traziam o sinal prático do conteúdo. Em Strategy
× State, a pergunta é quem inicia a troca de comportamento. Em Adapter × Bridge, é
quando as duas interfaces surgiram.

O cenário 4 descrevia o erro do conteúdo verificado: manter o if/else no Context e
criar Adapter quando o sistema controla a classe adaptada. Havia uma imprecisão em
`s4_uso_incorreto_strategy`: a frase "o if/else deve ser movido para as estratégias"
está errada. O certo é o cliente escolher e injetar a estratégia no Context. O
guardião não viu o problema.

### 4.3 Aderência à pergunta

A aderência era alta nos cenários 1, 2, 4 e 5. Era parcial nos cenários 3 e 7. No
cenário 3, a pergunta pedia duas situações explícitas, uma de uso e uma de evitação, e
a aula entregava o critério espalhado. No cenário 7, a resposta era a aula completa,
com o essencial distribuído entre "O preço", "O erro que se comete" e "Não confunda".

A causa era o formato fixo de seis seções: o 7B ignorava a instrução de abrir com uma
frase que respondesse à pergunta. A versão atual trocou esse formato por intenções e
respostas curtas, justamente para evitar esse desvio.

### 4.4 Exercício e diagnóstico

Os dois exercícios tinham 182 e 186 palavras, sem código e sem solução, com cenário,
tarefa, três critérios e duas perguntas de reflexão. O cenário era diferente do
exemplo da aula.

Na primeira execução de `s8_exercicio_adapter`, o nome "Adapter" apareceu nas
perguntas de reflexão. O guardião respondeu `OK` e não viu. A regra do prompt passou a
proibir `Strategy`, `Adapter`, `Context`, `Target` e `Adaptee` em qualquer parte do
exercício. A versão atual também verifica isso em Python.

As duas avaliações citavam o trecho do estudante antes de julgar. A de Adapter
reconheceu a interface única e apontou o que faltou. A de Strategy dizia que o
estudante "não mencionou" a escolha pelo cliente, embora ele tivesse escrito que o
contexto receberia a implementação pronta e poderia trocá-la. Era uma limitação do
inquiridor.

### 4.5 Recusas determinísticas

Os pedidos de invenção (6a) e de solução pronta (6b) foram recusados em menos de um
segundo, sem chamada ao modelo. A versão atual mantém as duas recusas e acrescenta a
recusa de padrões GoF fora do escopo.

### 4.6 O que o guardião viu e o que passou

No lote final todos os pareceres foram `OK`, mas isso não quer dizer que tudo estava
perfeito. Ele não viu o vazamento de "Adapter" no exercício nem a imprecisão de
`s4_uso_incorreto_strategy`.

Antes do ajuste, no modo exercício, ele respondia ao exercício em vez de revisar. O
formato virou uma lista (a) a (e) com `ok/falha`, o que torna o parecer verificável.
Nas aulas, os pareceres citavam participantes, consequências e a distinção com
State/Bridge.

### 4.7 Síntese da primeira versão

| Dimensão | Resultado |
|---|---|
| Correção conceitual | 14 de 14 aulas alinhadas ao conteúdo verificado; 1 imprecisão localizada |
| Profundidade | 881 a 1.142 palavras por aula, com mecanismo, custo e erro comum |
| Aderência | alta em 4 categorias; parcial em seleção e fechamento |
| Exercício | sem código e sem solução; vazamento do nome corrigido e reexecutado |
| Diagnóstico | feedback citado e específico; 1 julgamento parcialmente injusto |
| Anti-alucinação | 2 recusas instantâneas, sem chamada ao modelo |
| Custo | zero; nenhuma chamada externa durante a execução |

## 5. Confiabilidade do guardião

O guardião não é um oráculo. É outro modelo 7B, com os mesmos limites. Ele serve para
chamar atenção a erros que passariam despercebidos, não para garantir que a resposta
esteja certa.

### 5.1 Acertos

Em 05/11, às 16:29, a mini-aula falava de navegação, mas o exemplo Java ainda era de
frete (`Frete`, `Sedex`). O guardião respondeu `CORRIGIR` e apontou a mistura. O
conteúdo foi alinhado ao domínio de navegação (`RotaStrategy`, `Navegador`).

Em 06/11, às 10:05, o parecer sobre a aula de Strategy foi `OK: O padrão descrito e o
exemplo em Java são corretos e consistentes. Não há erros ou invenções.`

### 5.2 Falsos negativos

Em 05/11, às 16:33, o exemplificador repetiu quase palavra por palavra a seção "O
problema" antes do código. O guardião respondeu `OK`. A correção foi determinística: o
Python passou a cortar qualquer prefixo antes do primeiro bloco.

Em 05/11, às 16:39, a explicação do Adapter não deixava claro quando as duas
interfaces já existiam. O guardião respondeu `OK`. O campo `sinal_pratico` foi
acrescentado ao conteúdo.

### 5.3 Falso positivo

Em 05/11, às 16:36, o guardião leu o if/else de "O problema" como se fosse a solução
final e respondeu `CORRIGIR`. Ali o if/else é a solução ingênua que o padrão
substitui. O prompt passou a separar a solução ingênua do código entregue.

### 5.4 Formato

Entre 16:41 e 16:48, o guardião copiava o exercício. O formato passou a terminar em
`VEREDITO: OK` ou `VEREDITO: CORRIGIR`, e o Python extrai o último marcador.

Às 16:42, na avaliação, ele sugeriu `EntregaStrategy` e `EntregaCarro`, embora o
feedback não devesse entregar nomes. A tarefa de revisão passou a proibir nomes de
classes e a verificar se o feedback é fiel ao cenário.

### 5.5 Conclusão

O guardião funciona como segunda leitura, não como garantia. A confiabilidade vem de
três camadas determinísticas: o conteúdo verificado, os validadores e o fallback; os
testes cobrem o que não depende do modelo.

## 6. Limitações

- O 7B varia entre execuções e às vezes repete trechos.
- O Java é verificado e há teste de compilação quando `javac` está instalado; no
  ambiente principal não há JDK.
- O guardião pode errar para mais e para menos.
- `num_ctx=8192` depende do repasse pelo LiteLLM.
- O Gradio é opcional.
- A tabela da versão atual ainda precisa ser preenchida.

## 7. Como reproduzir

```powershell
cd C:\Users\ratoyy\qwen_stg

# testes sem modelo
.\.venv\Scripts\python.exe -m unittest discover -s testes -v

# cenários do roteiro
.\.venv\Scripts\python.exe docs\rodar_cenarios.py

# exercício e avaliação, com memória
.\.venv\Scripts\python.exe docs\rodar_avaliacoes.py

# resumo das saídas
.\.venv\Scripts\python.exe docs\resumir_cenarios.py
```

Os arquivos de `evidencias/cenarios/` guardam a saída exata de cada execução.
`evidencias/execucoes.jsonl` guarda data, intenção, padrão, pergunta, tempo e parecer
do guardião.
