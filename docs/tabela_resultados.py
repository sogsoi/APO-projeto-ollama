"""Monta a tabela de resultados do caderno a partir das evidências.

Uso:
    .\\.venv\\Scripts\\python.exe docs\\tabela_resultados.py

Lê `evidencias/cenarios/*.txt`, o tempo em `*.err` e o parecer em
`evidencias/execucoes.jsonl`. Imprime as linhas em Markdown.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from rodar_cenarios import CENARIOS

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "evidencias" / "cenarios"
LOG = RAIZ / "evidencias" / "execucoes.jsonl"


def tempo_do_err(arquivo: Path) -> str:
    caminho = arquivo.with_suffix(".err")
    if not caminho.exists():
        return "?"
    bytes_ = caminho.read_bytes()
    if bytes_[:2] in (b"\xff\xfe", b"\xfe\xff"):
        texto = bytes_.decode("utf-16", errors="replace")
    else:
        texto = bytes_.decode("utf-8", errors="replace")
    achado = re.search(r"\(tempo: (\d+)s\)", texto)
    return f"{achado.group(1)} s" if achado else "?"


def registros_por_pergunta() -> dict[str, dict]:
    mapa: dict[str, dict] = {}
    if not LOG.exists():
        return mapa
    for linha in LOG.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        item = json.loads(linha)
        mapa[item.get("pergunta", "")] = item
    return mapa


def main() -> None:
    registros = registros_por_pergunta()
    print("| Cenário | Tempo | Palavras | Estrutura | Intenção | Parecer |")
    print("|---|---|---|---|---|---|")
    for nome, pergunta in CENARIOS:
        arquivo = PASTA / f"{nome}.txt"
        if not arquivo.exists():
            continue
        texto = arquivo.read_text(encoding="utf-8")
        java = texto.count("```java")
        if java:
            estrutura = f"{java} bloco(s) Java"
        elif "Minha resposta" in texto:
            estrutura = "exercício"
        elif len(texto.split()) < 80:
            estrutura = "recusa determinística"
        else:
            estrutura = "texto"
        registro = registros.get(pergunta, {})
        intencao = registro.get("intencao") or registro.get("modo") or "—"
        parecer = registro.get("parecer") or registro.get("erro") or "(sem parecer)"
        parecer = str(parecer).replace("|", "\\|")
        print(
            f"| `{nome}` | {tempo_do_err(arquivo)} | {len(texto.split())} | "
            f"{estrutura} | {intencao} | {parecer[:120]} |"
        )


if __name__ == "__main__":
    main()
