"""Gera qwen_stg.py, a versão tudo-em-um do tutor, a partir dos módulos de agente/.

Uso:
    python docs/gerar_arquivo_unico.py

O arquivo gerado é para leitura e envio a outra IA; a implementação canônica
continua em agente/. Não chama o modelo.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "qwen_stg.py"

MODULOS = (
    "agente/conhecimento.py",
    "agente/estado.py",
    "agente/prompts.py",
    "agente/validadores.py",
    "agente/roteador.py",
    "agente/motor.py",
    "agente/tutor.py",
    "agente/chat.py",
    "agente/__main__.py",
)

CABECALHO = '''"""Tutor multiagente de Strategy e Adapter, em um único arquivo.

Gerado por docs/gerar_arquivo_unico.py a partir de agente/. A implementação
canônica, testada, está em agente/. Este arquivo serve para leitura e para
envio a outra IA.

Uso:
    python qwen_stg.py "O que é Strategy?"
    python qwen_stg.py
    python qwen_stg.py --chat
"""

'''


def _imports_e_corpo(caminho: Path) -> tuple[list[str], list[str]]:
    texto = caminho.read_text(encoding="utf-8")
    arvore = ast.parse(texto)
    linhas = texto.splitlines()
    descartar: set[int] = set()

    if arvore.body and isinstance(arvore.body[0], ast.Expr):
        valor = arvore.body[0].value
        if isinstance(valor, ast.Constant) and isinstance(valor.value, str):
            descartar.update(range(arvore.body[0].lineno, arvore.body[0].end_lineno + 1))

    imports: list[str] = []
    for no in arvore.body:
        if not isinstance(no, (ast.Import, ast.ImportFrom)):
            continue
        descartar.update(range(no.lineno, no.end_lineno + 1))
        if isinstance(no, ast.ImportFrom):
            if no.module == "__future__" or no.level:
                continue
            nomes = ", ".join(
                a.name + (f" as {a.asname}" if a.asname else "") for a in no.names
            )
            imports.append(f"from {no.module} import {nomes}")
        else:
            nomes = ", ".join(
                a.name + (f" as {a.asname}" if a.asname else "") for a in no.names
            )
            imports.append(f"import {nomes}")

    corpo = [linha for i, linha in enumerate(linhas, start=1) if i not in descartar]
    texto_corpo = "\n".join(corpo).strip()
    texto_corpo = texto_corpo.replace("        from .chat import abrir\n", "")
    return imports, [texto_corpo]


def main() -> None:
    imports: list[str] = []
    corpos: list[str] = []
    for caminho in MODULOS:
        imps, corpo = _imports_e_corpo(RAIZ / caminho)
        for item in imps:
            if item not in imports:
                imports.append(item)
        corpos.extend(corpo)

    imports.sort(key=lambda item: (not item.startswith("import "), item))
    partes = [
        CABECALHO + "from __future__ import annotations",
        "",
        *imports,
        "",
        "\n\n".join(corpos).strip(),
        "",
    ]
    SAIDA.write_text("\n".join(partes), encoding="utf-8")
    print(f"Gerado: {SAIDA}")


if __name__ == "__main__":
    sys.exit(main())
