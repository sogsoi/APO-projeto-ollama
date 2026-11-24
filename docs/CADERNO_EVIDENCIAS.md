# Caderno de evidências

Trabalho de ELC1070, Análise e Projeto de Sistemas OO.
Sistema: tutor multiagente de Strategy e Adapter (CrewAI + Ollama).

> **Nota sobre as versões.** A seção 3 reúne os resultados executados na **versão atual**
> do sistema (intenções, fatos por tópico, validadores determinísticos e fallback
> verificado), rodando em 24/11/2026 com `qwen2.5:7b` em GPU local. A seção 4 mantém,
> como histórico comparativo, os resultados da primeira versão (três modos e mini-aula
> de seis seções).

## 1. Ambiente

| Item | Ambiente de desenvolvimento (v1) | Ambiente de execução dos cenários atuais (v2) |
|---|---|---|
| CPU | Intel Core i5-6400 (4 núcleos, 2,7 GHz) | AMD Ryzen 5 5600 (6 núcleos) |
| RAM | 16 GB | 16 GB |
| GPU | NVIDIA GeForce GTX 1070 (8 GB VRAM) | AMD Radeon RX 9060 XT |
| Sistema | Windows 11 | Windows 11 |
| Python | 3.13.16 em `.venv` | 3.12.1 em `.venv` |
| CrewAI | 1.15.35 | 1.15.35 |
| Modelo | `qwen2.5:7b` Q4_K_M | `qwen2.5:7b` Q4_K_M (`5,1 GB` em VRAM) |
| Inferência | Ollama 0.40.14, 100% GPU (Vulkan), contexto 8192 | Ollama 0.40.18, 100% GPU (Vulkan), contexto 8192 |

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

## 3. Roteiro e resultados da versão atual (24/11/2026)

| # | Cenário | Pergunta | Intenção obtida | Status |
|---|---|---|---|---|
| 1 | Conceito / Problema | "Explique o padrão X e qual problema ele resolve." | `problema` | executado |
| 2 | Exemplo | "Dê um exemplo de aplicação do padrão X em Java." | `exemplo` | executado |
| 3 | Seleção | "Descreva uma situação em que X é a melhor escolha e uma em que ele deve ser evitado." | `quando` | executado |
| 4 | Uso incorreto | "Como X costuma ser aplicado de forma errada? Como corrigir?" | `erro` | executado |
| 5 | Confusão | "Com qual padrão X é mais confundido? Qual a diferença?" | `confusoes` | executado |
| 6a | Anti-alucinação | "Invente um padrão chamado Z e explique para mim." | `invencao` (recusa) | executado |
| 6b | Anti-alucinação | "Me entregue o código pronto de uma solução completa." | `solucao_pronta` (recusa) | executado |
| 6c | Fora do escopo | "Explique o Observer." | `fora_escopo` (conversa) | executado |
| 7 | Fechamento | "O que devo lembrar antes de usar o padrão X?" | `fechamento` | executado |
| 8 | Exercício | "Me dê um exercício sobre o padrão X." | `exercicio` | executado |
| 9 | Diagnóstico | "Minha resposta: ..." (depois do exercício) | `avaliacao` | executado |
| 10 | Comparação | "Qual a diferença entre Strategy e Adapter?" | `comparar` | executado |
| 11 | Abandono | "Quero outro tópico" (com exercício pendente) | `abandonar_exercicio` (sem modelo) | executado |

### 3.1 Tabela de resultados da versão atual

Todos os 21 cenários abaixo foram executados em 24/11/2026 com `qwen2.5:7b` (100% GPU, contexto 8192) e encerraram com código de saída `0`. As saídas completas estão em `evidencias/cenarios/` e o log estruturado em `evidencias/execucoes.jsonl`.

| # | Cenário | Padrão | Intenção (rota) | Tempo | Palavras | Tent. | Fallback | Parecer do Guardião | Correção / Utilidade |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `s1_conceito_strategy` | Strategy | `problema` (regras) | 39,9 s | 94 | 2 | sim | CORRIGIR (pediu mais detalhes) | Correta / Alta (fallback verificado) |
| 1 | `s1_conceito_adapter` | Adapter | `problema` (regras) | 22,4 s | 79 | 2 | sim | CORRIGIR (omissão) | Correta / Alta (fallback verificado) |
| 2 | `s2_exemplo_strategy` | Strategy | `exemplo` (regras) | 17,7 s | 366 | 1 | não | OK | Correta / Alta (Java verificado + UML) |
| 2 | `s2_exemplo_adapter` | Adapter | `exemplo` (regras) | 17,5 s | 347 | 1 | não | OK | Correta / Alta (Java verificado + UML) |
| 3 | `s3_selecao_strategy` | Strategy | `quando` (llm) | 16,7 s | 159 | 1 | não | OK | Correta / Alta |
| 3 | `s3_selecao_adapter` | Adapter | `quando` (llm) | 15,3 s | 98 | 1 | não | OK | Correta / Alta |
| 4 | `s4_uso_incorreto_strategy` | Strategy | `erro` (llm) | 18,8 s | 87 | 2 | não | OK (após regeneração) | Correta / Alta |
| 4 | `s4_uso_incorreto_adapter` | Adapter | `erro` (llm) | 14,3 s | 110 | 1 | não | OK | Correta / Alta |
| 5 | `s5_confusao_strategy` | Strategy | `confusoes` (regras) | 17,8 s | 143 | 2 | sim | CORRIGIR (omissão State) | Correta / Alta (fallback verificado) |
| 5 | `s5_confusao_adapter` | Adapter | `confusoes` (regras) | 19,2 s | 101 | 2 | não | OK (corrigiu confusão na 2ª tent.) | Correta / Alta |
| 6a | `s6a_invencao` | — | `invencao` (regras) | 0,0 s | 33 | 0 | não | sem modelo | Correta / Alta (recusa imediata) |
| 6b | `s6b_solucao_pronta` | — | `solucao_pronta` (regras) | 0,0 s | 35 | 0 | não | sem modelo | Correta / Alta (recusa imediata) |
| 6c | `s6c_fora_escopo` | — | `fora_escopo` (conversa) | 12,1 s | 59 | 1 | não | sem guardião (conversa) | Correta / Alta (recusou Observer) |
| 7 | `s7_fechamento_strategy` | Strategy | `fechamento` (regras) | 18,2 s | 115 | 1 | não | OK | Correta / Alta |
| 7 | `s7_fechamento_adapter` | Adapter | `fechamento` (regras) | 18,1 s | 86 | 2 | não | OK (após regeneração) | Correta / Alta |
| 8 | `s8_exercicio_strategy` | Strategy | `exercicio` (regras) | 19,5 s | 163 | 1 | não | OK (sem vazamento) | Correta / Alta |
| 8 | `s8_exercicio_adapter` | Adapter | `exercicio` (regras) | 19,2 s | 147 | 1 | não | OK (sem vazamento) | Correta / Alta |
| 9 | `s9_avaliacao_strategy` | Strategy | `exercicio` + `avaliacao` | 42,5 s | 275 | 2 + 1 | sim (ex.) / não (av.) | CORRIGIR (ex.) / OK (av.) | Parcial / Média-Alta (ver análise) |
| 9 | `s9_avaliacao_adapter` | Adapter | `exercicio` + `avaliacao` | 36,2 s | 287 | 2 + 1 | sim (ex.) / não (av.) | CORRIGIR (ex.) / OK (av.) | Parcial / Média-Alta (ver análise) |
| 10 | `s10_comparacao` | ambos | `comparar` (regras) | 29,5 s | 176 | 2 | não | OK (corrigiu "Context" no Adapter) | Correta / Alta |
| 11 | `s11_abandono` | Strategy | `exercicio` + `abandonar` | 29,8 s + 0,0 s | 190 | 2 + 0 | sim (ex.) / não (ab.) | validador bloqueou vazamento | Correta / Alta |

### 3.2 Análise qualitativa da versão atual

- **Ganho de velocidade e objetividade:** Em comparação com a v1 (72 s a 141 s e 881 a 1.142 palavras por resposta), a versão atual respondeu entre **14 s e 29 s** (39,9 s no primeiro aquecimento) com textos curtos de **79 a 176 palavras**, sempre aderentes à pergunta e terminando com uma pergunta de reflexão.
- **Eficácia das três camadas de confiabilidade:**
  - *Regeneração (2ª tentativa):* corrigiu erros reais em 4 cenários (`s4_uso_incorreto_strategy`, `s5_confusao_adapter`, `s7_fechamento_adapter` e `s10_comparacao`). Em `s5_confusao_adapter`, o guardião detectou na 1ª tentativa uma confusão entre Adapter e Strategy ("mudar a interface") e a 2ª tentativa foi aprovada corretamente. Em `s10_comparacao`, o guardião barrou o uso incorreto de `Context` no Adapter.
  - *Validadores determinísticos e fallback:* garantiram que **nenhum** exercício entregue ao estudante vazasse o nome do padrão ou código Java. Em `s11_abandono`, o validador Python pegou o vazamento dos termos `Strategy` e `Context` (mesmo com o guardião retornando `OK`) e acionou o exercício fixo verificado.
  - *Exemplos Java e recusas:* Os dois exemplos (`s2`) exibiram exatamente o código Java verificado com diagrama UML e comentários fiéis; `6a` e `6b` recusaram em `0,0 s` sem chamar o modelo; `6c` recusou `Observer` educadamente sem explicá-lo; `11` limpou o exercício pendente em `0,0 s`.
- **Limitações observadas no modelo 7B (evidências para melhoria):**
  - *Placeholder literal no feedback (`s9`):* Nas duas sessões de avaliação (`s9_avaliacao_strategy` e `s9_avaliacao_adapter`), o modelo copiou literalmente o texto de instrução `"trecho literal da resposta, até 30 palavras"` na linha `**O que você escreveu:**`, embora o diagnóstico nos blocos seguintes tenha sido pertinente e as linhas internas `RESULTADO:` e `CONCEITO:` tenham sido corretamente ocultadas da saída visível.
  - *Falso positivo do guardião em exercícios (`s9`):* O guardião às vezes interpretou o critério `(c) não revela o nome do padrão` ao contrário, reprovando exercícios bons por "não mencionarem `Context` ou `Strategy`". Nesses casos o fallback garantiu um exercício válido.
  - *Prioridade de palavras-chave no roteador (`s1`):* A pergunta *"Explique o padrão X e qual problema ele resolve"* casou duas palavras-chave de `problema` (`problema` e `resolve`) contra uma de `conceito` (`explique`), sendo roteada para `problema` em vez de `contexto`.

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
- No feedback de avaliação (`s9`), o modelo 7B ocasionalmente copia o placeholder `"trecho literal da resposta, até 30 palavras"` em vez de citar a frase do aluno; o validador pode ser estendido para rejeitar esse texto literal.

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
