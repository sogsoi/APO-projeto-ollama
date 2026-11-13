"""Gera docs/PROMPTS.md a partir de agente/prompts.py.

Uso:
    .\\.venv\\Scripts\\python.exe docs\\gerar_prompts.py

Não chama o modelo; só lê os textos dos agentes e das tarefas para a
documentação não ficar desatualizada.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from agente.conhecimento import DESCRICAO_INTENCAO, TOPICOS_POR_INTENCAO  # noqa: E402
from agente.motor import CHAVES  # noqa: E402
from agente.prompts import AGENTES, INSTRUCOES_INTENCAO, REGRAS, TAREFAS  # noqa: E402
from agente.roteador import ORDEM_DESEMPATE, PALAVRAS_POR_INTENCAO  # noqa: E402

SAIDA = Path(__file__).resolve().parent / "PROMPTS.md"

DESCRICAO_VARIAVEIS = {
    "fatos": "fatos verificados dos tópicos que a intenção pede",
    "estado": "resumo do aluno: tópicos vistos, dificuldades, exercício pendente",
    "historico": "últimas mensagens, truncadas por tamanho",
    "pergunta": "mensagem atual do estudante",
    "instrucao": "o que a intenção exige do tutor",
    "padrao_nome": "Strategy, Adapter ou 'Strategy e Adapter'",
    "estrategia": "pedagogia própria do padrão (gancho e abordagem)",
    "abertura": "como abrir a resposta conforme o que o aluno já viu",
    "limite": "alvo de palavras da explicação",
    "pergunta_final": "pergunta sugerida para fechar a aula",
    "correcao": "correção obrigatória quando a primeira versão é rejeitada",
    "codigo": "exemplo Java verificado, exibido ao aluno",
    "dominio": "domínio do exercício",
    "exercicio": "exercício pendente, no momento da avaliação",
    "extra": "checagem adicional do guardião para aquela tarefa",
}


def bloco(texto: str) -> str:
    return "```text\n" + texto.strip() + "\n```"


def main() -> None:
    linhas: list[str] = [
        "# Prompts dos agentes",
        "",
        "Gerado por `docs/gerar_prompts.py` a partir de `agente/prompts.py`. As variáveis",
        "são preenchidas no `kickoff` do CrewAI.",
        "",
        "## Variáveis de entrada",
        "",
        "| Variável | Conteúdo |",
        "|---|---|",
    ]
    for chave in CHAVES:
        linhas.append(f"| `{{{chave}}}` | {DESCRICAO_VARIAVEIS.get(chave, '')} |")

    linhas.extend([
        "",
        "## Regras comuns",
        "",
        "Entram no backstory de todos os agentes.",
        "",
        bloco(REGRAS),
        "",
        "## Agentes",
        "",
        "| Agente | Papel | Objetivo |",
        "|---|---|---|",
    ])
    for nome, a in AGENTES.items():
        linhas.append(f"| `{nome}` | {a['role']} | {a['goal']} |")

    for nome, a in AGENTES.items():
        linhas.extend([
            "",
            f"### {nome}",
            "",
            "**Papel (role):** " + a["role"],
            "",
            "**Objetivo (goal):**",
            "",
            bloco(a["goal"]),
            "",
            "**História (backstory):**",
            "",
            bloco(a["backstory"] + "\n\n" + REGRAS),
        ])

    linhas.extend([
        "",
        "## Instruções por intenção",
        "",
        "| Intenção | O que pedir | Tópicos de fatos injetados |",
        "|---|---|---|",
    ])
    for intencao, instrucao in INSTRUCOES_INTENCAO.items():
        topicos = ", ".join(TOPICOS_POR_INTENCAO.get(intencao, ())) or "—"
        descricao = DESCRICAO_INTENCAO.get(intencao, "resposta à dúvida do aluno")
        linhas.append(f"| `{intencao}` | {descricao}: {instrucao} | {topicos} |")

    linhas.extend([
        "",
        "## Tarefas",
        "",
        "Cada tarefa é usada em uma etapa do fluxo. O guardião recebe o texto produzido",
        "na tarefa anterior e devolve um parecer interno.",
        "",
    ])
    for tid, t in TAREFAS.items():
        linhas.extend([
            f"### `{tid}` (agente: `{t['agente']}`)",
            "",
            "**Descrição:**",
            "",
            bloco(t["descricao"]),
            "",
            "**Saída esperada:**",
            "",
            bloco(t["saida"]),
            "",
        ])

    linhas.extend([
        "## Roteamento sem o modelo",
        "",
        "As regras abaixo rodam antes de qualquer chamada ao LLM. O agente Roteador só é",
        "consultado quando nenhuma delas casa.",
        "",
        "| Intenção | Palavras-chave |",
        "|---|---|",
    ])
    for intencao in ORDEM_DESEMPATE:
        palavras = ", ".join(f"`{p}`" for p in PALAVRAS_POR_INTENCAO.get(intencao, ()))
        linhas.append(f"| `{intencao}` | {palavras} |")

    linhas.extend([
        "",
        "Além das palavras-chave, o roteador trata:",
        "",
        "- resposta a exercício pendente: usa o padrão do exercício e vai para avaliação;",
        "- abandono do exercício: pedidos como \"outro tópico\" ou \"pular\";",
        "- recusa de invenção: \"invente um padrão\" (sem negação) recebe resposta fixa;",
        "- recusa de solução pronta: \"resolva para mim\" recebe resposta fixa;",
        "- padrão fora do escopo: outros padrões GoF são recusados com honestidade;",
        "- saudação e pedido de esclarecimento sem padrão definido.",
        "",
        "## Validação e fallback",
        "",
        "- Toda saída passa por validadores determinísticos antes do guardião.",
        "- O guardião devolve `VEREDITO: OK` ou `VEREDITO: CORRIGIR`; em caso de correção,",
        "  o produtor tenta mais uma vez com a correção obrigatória.",
        "- Se as duas tentativas falharem, entra um fallback montado só com os fatos",
        "  verificados. No exercício, o fallback é o exercício fixo do padrão.",
        "- As decisões e os pareceres vão para `evidencias/execucoes.jsonl`.",
        "",
    ])

    SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Gerado: {SAIDA}")


if __name__ == "__main__":
    main()
