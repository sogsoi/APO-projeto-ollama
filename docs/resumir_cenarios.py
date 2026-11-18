"""Resume as saídas dos cenários para o caderno de evidências.

Uso:
    .\\.venv\\Scripts\\python.exe docs\\resumir_cenarios.py

Grava `evidencias/cenarios/_resumo.txt` com tamanho, presença de Java,
vazamento do nome do padrão nos exercícios e pareceres registrados.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "evidencias" / "cenarios"
LOG = RAIZ / "evidencias" / "execucoes.jsonl"
SAIDA = PASTA / "_resumo.txt"


def ler_texto(arquivo: Path) -> str:
    try:
        return arquivo.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        return arquivo.read_text(encoding="utf-16", errors="replace").strip()


def ler_pareceres() -> list[dict]:
    if not LOG.exists():
        return []
    linhas = LOG.read_text(encoding="utf-8").splitlines()
    return [json.loads(linha) for linha in linhas if linha.strip()]


def resumo(arquivo: Path) -> list[str]:
    texto = ler_texto(arquivo)
    if not texto:
        return []

    nome = arquivo.stem
    linhas = [
        f"### {nome}",
        f"palavras: {len(texto.split())}",
        f"blocos java: {texto.count('```java')}",
        f"início: {' '.join(texto.split())[:200]}",
    ]

    if "exercicio" in nome:
        vazou = re.findall(r"\b(Strategy|Adapter)\b", texto)
        linhas.append(f"nome do padrão no enunciado: {sorted(set(vazou)) or 'não'}")
        linhas.append(f"tem bloco de código: {'sim' if '```' in texto else 'não'}")

    if "avaliacao" in nome:
        linhas.append(f"RESULTADO visível: {'sim' if 'RESULTADO:' in texto else 'não'}")

    linhas.append("")
    return linhas


def main() -> None:
    saida: list[str] = []
    for arquivo in sorted(PASTA.glob("*.txt")):
        if arquivo.name.startswith("_"):
            continue
        saida.extend(resumo(arquivo))

    saida.append("## Pareceres registrados")
    saida.append("")
    for item in ler_pareceres():
        intencao = item.get("intencao") or item.get("modo") or "?"
        padrao = item.get("padrao") or "—"
        parecer = item.get("parecer") or item.get("erro") or "(sem parecer)"
        saida.append(
            f"- {item.get('data_hora', '')[:19]} | {padrao} | {intencao} | "
            f"{item.get('duracao_s', 0):.1f}s | {item.get('pergunta', '')[:70]}"
        )
        saida.append(f"  parecer: {str(parecer)[:240]}")

    texto = "\n".join(saida) + "\n"
    SAIDA.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
