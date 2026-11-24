"""Motor de execução: único ponto que fala com CrewAI/Ollama (tudo local, custo zero)."""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.request
from typing import Protocol
from urllib.parse import urlparse

from .prompts import AGENTES, REGRAS, REGRAS_EXERCICIO, TAREFAS

# Recomendação da disciplina, em ordem de preferência. Não é uma lista fechada:
# se nenhum destes estiver instalado, o motor usa outro modelo de conversa e avisa.
MODELOS_RECOMENDADOS = ("qwen2.5:7b", "qwen2.5:3b")

# Janela de contexto (prompt + resposta) enviada ao Ollama. O padrão do Ollama
# pode ser 2048/4096 e truncaria as regras, os fatos e o histórico.
NUM_CTX = 8192
TIMEOUT_DETECCAO = 2.0
TIMEOUT_LLM = 300
MAX_TOKENS = 1200

CHAVES = ("fatos", "estado", "historico", "pergunta", "instrucao", "padrao_nome",
          "estrategia", "abertura", "limite", "pergunta_final", "correcao", "codigo",
          "dominio", "exercicio", "extra")

_log = logging.getLogger(__name__)


class ModeloIndisponivel(RuntimeError):
    """O Ollama não respondeu ou não há um modelo de conversa instalado."""


def _base_url() -> str:
    """Lê OLLAMA_HOST e devolve uma URL completa, com porta padrão 11434."""
    bruto = (os.environ.get("OLLAMA_HOST") or "").strip() or "127.0.0.1:11434"
    if bruto.startswith(":"):
        bruto = "127.0.0.1" + bruto
    if not bruto.startswith(("http://", "https://")):
        bruto = "http://" + bruto

    try:
        partes = urlparse(bruto)
        porta = partes.port
    except ValueError as erro:
        raise ModeloIndisponivel(f"OLLAMA_HOST inválido: {bruto!r}") from erro

    if not partes.netloc:
        raise ModeloIndisponivel(f"OLLAMA_HOST inválido: {bruto!r}")

    netloc = partes.netloc.replace("0.0.0.0", "127.0.0.1")
    if porta is None and partes.scheme == "http":
        netloc += ":11434"
    return f"{partes.scheme}://{netloc}".rstrip("/")


def _listar_instalados(base_url: str) -> list[str]:
    with urllib.request.urlopen(f"{base_url}/api/tags", timeout=TIMEOUT_DETECCAO) as resp:
        dados = json.load(resp)
    nomes = (m.get("name") or m.get("model") or "" for m in dados.get("models", []))
    return [nome for nome in nomes if nome]


def _nome_curto(nome: str) -> str:
    """Remove prefixo de registry: registry:5000/qwen2.5:7b -> qwen2.5:7b."""
    return nome.rsplit("/", 1)[-1]


_MARCAS_EMBEDDING = ("embed", "bge", "minilm")


def _e_embedding(nome: str) -> bool:
    baixo = nome.lower()
    return any(marca in baixo for marca in _MARCAS_EMBEDDING)


def _tamanho_b(nome: str) -> float:
    achado = re.search(r"(\d+(?:\.\d+)?)b", nome.lower())
    return float(achado.group(1)) if achado else 0.0


def escolher_modelo(instalados: list[str]) -> str | None:
    """Escolhe um modelo de conversa: recomendados primeiro, depois qualquer um."""
    conversa = [n for n in instalados if n and not _e_embedding(n)]

    for pref in MODELOS_RECOMENDADOS:          # 1. nome exato (7b antes de 3b)
        for nome in conversa:
            if _nome_curto(nome) == pref:
                return nome

    for pref in MODELOS_RECOMENDADOS:          # 2. variante do recomendado
        for nome in conversa:
            if _nome_curto(nome).startswith(pref):
                return nome

    qwen = [n for n in conversa if _nome_curto(n).lower().startswith("qwen")]
    if qwen:                                    # 3. outro qwen, do maior para o menor
        return max(qwen, key=lambda n: _tamanho_b(_nome_curto(n)))

    if conversa:                                # 4. qualquer modelo, do maior para o menor
        return max(conversa, key=lambda n: _tamanho_b(_nome_curto(n)))
    return None


def _modelo_forcado() -> str | None:
    bruto = (os.environ.get("MODELO_LLM") or "").strip()
    return _nome_curto(bruto.removeprefix("ollama/")) if bruto else None


def detectar_modelo(base_url: str | None = None) -> str:
    """Devolve 'ollama/<modelo>' do melhor modelo instalado, sem fixar o 7B."""
    base = (base_url or _base_url()).rstrip("/")

    try:
        instalados = _listar_instalados(base)
    except Exception as erro:
        raise ModeloIndisponivel(
            f"Não consegui falar com o Ollama em {base}.\n"
            "Verifique se ele está rodando (ollama ps) e tente de novo."
        ) from erro

    forcado = _modelo_forcado()
    if forcado:
        if _e_embedding(forcado):
            raise ModeloIndisponivel(
                f"MODELO_LLM='{forcado}' não é um modelo de conversa."
            )
        exato = next((n for n in instalados if _nome_curto(n) == forcado), None)
        if exato is None:
            exato = next((n for n in instalados if _nome_curto(n).startswith(forcado)), None)
        if exato is None:
            raise ModeloIndisponivel(
                f"MODELO_LLM='{forcado}' não está instalado.\n"
                f"Rode: ollama pull {forcado}"
            )
        escolhido = _nome_curto(exato)
    else:
        encontrado = escolher_modelo(instalados)
        if encontrado is None:
            raise ModeloIndisponivel(
                "Nenhum modelo de conversa está instalado.\n"
                "Rode um destes:\n  ollama pull qwen2.5:3b\n  ollama pull qwen2.5:7b"
            )
        escolhido = _nome_curto(encontrado)

    if not any(escolhido == p or escolhido.startswith(p) for p in MODELOS_RECOMENDADOS):
        _log.warning(
            "Usando %s, que não está na lista recomendada (%s). "
            "A qualidade pedagógica pode variar.",
            escolhido, ", ".join(MODELOS_RECOMENDADOS),
        )
    return f"ollama/{escolhido}"


def _normalizar_modelo(modelo: str) -> str:
    modelo = modelo.strip()
    return modelo if modelo.startswith("ollama/") else f"ollama/{modelo}"


class Motor(Protocol):
    def rodar(self, tarefas: list[str], inputs: dict[str, str]) -> list[str]: ...


class MotorCrewAI:
    """Monta uma Crew sequencial com as tarefas pedidas e devolve a saída de cada uma."""

    def __init__(self, modelo: str | None = None, base_url: str | None = None) -> None:
        self.modelo = _normalizar_modelo(modelo) if modelo else None
        self.base_url = base_url.rstrip("/") if base_url else None
        self._llm = None

    def _criar_llm(self):
        # O import do CrewAI também carrega o .env. Por isso a detecção acontece
        # só aqui, na primeira chamada real ao modelo, e não no import do módulo.
        from crewai import LLM

        if self._llm is None:
            base = self.base_url or _base_url()
            modelo = self.modelo or detectar_modelo(base)
            self.base_url, self.modelo = base, modelo
            self._llm = LLM(model=modelo, base_url=base, is_litellm=True,
                            temperature=0.3, timeout=TIMEOUT_LLM, max_tokens=MAX_TOKENS,
                            num_ctx=NUM_CTX, context_window_size=NUM_CTX)
        return self._llm

    def rodar(self, tarefas: list[str], inputs: dict[str, str]) -> list[str]:
        from crewai import Agent, Crew, Process, Task

        llm = self._criar_llm()
        agentes: dict[str, Agent] = {}
        lista: list[Task] = []
        for tid in tarefas:
            t = TAREFAS[tid]
            nome = t["agente"]
            if nome not in agentes:
                a = AGENTES[nome]
                regras = REGRAS_EXERCICIO if tid == "exercicio" else REGRAS
                agentes[nome] = Agent(
                    role=a["role"], goal=a["goal"],
                    backstory=a["backstory"] + "\n\n" + regras,
                    llm=llm, allow_delegation=False, verbose=False,
                )
            lista.append(Task(description=t["descricao"], expected_output=t["saida"],
                              agent=agentes[nome]))
        crew = Crew(agents=list(agentes.values()), tasks=lista,
                    process=Process.sequential, verbose=False)
        valores = {k: "" for k in CHAVES}
        valores.update({k: str(v) for k, v in inputs.items()})
        resultado = crew.kickoff(inputs=valores)
        return [o.raw for o in resultado.tasks_output]
