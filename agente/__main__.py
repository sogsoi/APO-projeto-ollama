"""Ponto de entrada padronizado: python -m agente "pergunta" (ou sem argumento: conversa)."""

import logging
import sys
import time

from .tutor import Tutor


def _silenciar() -> None:
    for nome in ("crewai", "litellm", "LiteLLM", "httpx", "openai", "chromadb", "urllib3"):
        logging.getLogger(nome).setLevel(logging.ERROR)


def _responder(tutor: Tutor, pergunta: str) -> str:
    print("(consultando os agentes...)", file=sys.stderr, flush=True)
    inicio = time.perf_counter()
    try:
        return tutor.responder(pergunta)
    finally:
        print(f"(tempo: {time.perf_counter() - inicio:.0f}s)", file=sys.stderr, flush=True)


def main() -> None:
    _silenciar()
    args = sys.argv[1:]
    if "--chat" in args:
        from .chat import abrir
        abrir()
        return

    tutor = Tutor()
    pergunta = " ".join(args).strip()
    if pergunta or args:
        resposta = _responder(tutor, pergunta)
        print(resposta)
        sys.exit(0 if pergunta else 1)

    print("Tutor de padrões de projeto: Strategy e Adapter. Digite 'sair' para encerrar.\n")
    while True:
        try:
            entrada = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if entrada.lower() in {"sair", "exit", "quit"}:
            break
        print(f"\nTutor: {_responder(tutor, entrada)}\n")


if __name__ == "__main__":
    main()
