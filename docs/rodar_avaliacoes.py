"""Roda as sessões de exercício + avaliação pela CLI, com memória.

Uso:
    .\\.venv\\Scripts\\python.exe docs\\rodar_avaliacoes.py

Cada sessão manda três linhas para o chat: o pedido de exercício, a tentativa
de resposta e `sair`. A saída traz o exercício e o feedback.
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

SESSOES = (
    (
        "s9_avaliacao_strategy",
        [
            "Me dê um exercício sobre o padrão Strategy.",
            "Minha resposta: eu criaria uma interface comum para o cálculo, com "
            "implementações separadas para cada forma de calcular, e o contexto "
            "receberia a implementação pronta e poderia trocá-la sem if/else.",
            "sair",
        ],
    ),
    (
        "s9_avaliacao_adapter",
        [
            "Me dê um exercício sobre o padrão Adapter.",
            "Minha resposta: eu criaria uma interface única com o método que o "
            "sistema espera e duas classes adaptadoras, cada uma traduzindo a "
            "chamada para um serviço externo diferente, sem alterar esses serviços.",
            "sair",
        ],
    ),
)


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    ambiente = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")

    for nome, linhas in SESSOES:
        alvo = PASTA / f"{nome}.txt"
        if alvo.exists() and alvo.stat().st_size > 400:
            print(f"pulado (já existe): {nome}", flush=True)
            continue

        inicio = time.perf_counter()
        with alvo.open("w", encoding="utf-8") as saida, (
            PASTA / f"{nome}.err"
        ).open("w", encoding="utf-8") as erro:
            processo = subprocess.run(
                [str(PYTHON), "-m", "agente"],
                cwd=RAIZ,
                input="\n".join(linhas) + "\n",
                text=True,
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

    print("Avaliações concluídas.", flush=True)


if __name__ == "__main__":
    sys.exit(main())
