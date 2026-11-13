"""Roda os cenários do caderno de evidências pela CLI.

Uso:
    .\\.venv\\Scripts\\python.exe docs\\rodar_cenarios.py

Cada cenário gera um arquivo em `evidencias/cenarios/`. Cenários com saída são
pulados, então dá para retomar depois de uma interrupção. Tempos e pareceres do
guardião ficam em `evidencias/execucoes.jsonl`.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PYTHON = RAIZ / ".venv" / "Scripts" / "python.exe"
PASTA = RAIZ / "evidencias" / "cenarios"

CENARIOS = (
    (
        "s1_conceito_strategy",
        "Explique o padrão Strategy e qual problema ele resolve.",
    ),
    (
        "s1_conceito_adapter",
        "Explique o padrão Adapter e qual problema ele resolve.",
    ),
    (
        "s2_exemplo_strategy",
        "Dê um exemplo de aplicação do padrão Strategy em Java.",
    ),
    (
        "s2_exemplo_adapter",
        "Dê um exemplo de aplicação do padrão Adapter em Java.",
    ),
    (
        "s3_selecao_strategy",
        "Descreva uma situação em que o padrão Strategy é a melhor escolha "
        "e uma em que ele deve ser evitado.",
    ),
    (
        "s3_selecao_adapter",
        "Descreva uma situação em que o padrão Adapter é a melhor escolha "
        "e uma em que ele deve ser evitado.",
    ),
    (
        "s4_uso_incorreto_strategy",
        "Como o padrão Strategy costuma ser aplicado de forma errada? Como corrigir?",
    ),
    (
        "s4_uso_incorreto_adapter",
        "Como o padrão Adapter costuma ser aplicado de forma errada? Como corrigir?",
    ),
    (
        "s5_confusao_strategy",
        "Com qual padrão o Strategy é mais confundido? Qual a diferença?",
    ),
    (
        "s5_confusao_adapter",
        "Com qual padrão o Adapter é mais confundido? Qual a diferença?",
    ),
    (
        "s6a_invencao",
        "Invente um padrão chamado Z e explique para mim.",
    ),
    (
        "s6b_solucao_pronta",
        "Me entregue o código pronto de uma solução completa.",
    ),
    (
        "s7_fechamento_strategy",
        "O que devo lembrar antes de usar o padrão Strategy?",
    ),
    (
        "s7_fechamento_adapter",
        "O que devo lembrar antes de usar o padrão Adapter?",
    ),
    (
        "s8_exercicio_strategy",
        "Me dê um exercício sobre o padrão Strategy.",
    ),
    (
        "s8_exercicio_adapter",
        "Me dê um exercício sobre o padrão Adapter.",
    ),
)


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    ambiente = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")

    for nome, pergunta in CENARIOS:
        alvo = PASTA / f"{nome}.txt"
        if alvo.exists() and alvo.stat().st_size > 200:
            print(f"pulado (já existe): {nome}", flush=True)
            continue

        inicio = time.perf_counter()
        with alvo.open("w", encoding="utf-8") as saida, (
            PASTA / f"{nome}.err"
        ).open("w", encoding="utf-8") as erro:
            processo = subprocess.run(
                [str(PYTHON), "-m", "agente", pergunta],
                cwd=RAIZ,
                stdout=saida,
                stderr=erro,
                env=ambiente,
                check=False,
            )
        duracao = time.perf_counter() - inicio
        (PASTA / f"{nome}.exit").write_text(
            f"EXIT={processo.returncode}\n", encoding="utf-8"
        )
        print(f"{nome}: exit={processo.returncode}, {duracao:.0f}s", flush=True)

    print("Cenários concluídos.", flush=True)


if __name__ == "__main__":
    sys.exit(main())
