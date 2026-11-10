"""Motor de execução: único ponto que fala com CrewAI/Ollama (tudo local, custo zero)."""

from __future__ import annotations

from typing import Protocol

from .prompts import AGENTES, REGRAS, TAREFAS

MODELO = "ollama/qwen2.5:7b"
BASE_URL = "http://localhost:11434"
NUM_CTX = 8192

CHAVES = ("fatos", "estado", "historico", "pergunta", "instrucao", "padrao_nome",
          "estrategia", "abertura", "limite", "pergunta_final", "correcao", "codigo",
          "dominio", "exercicio", "extra")


class Motor(Protocol):
    def rodar(self, tarefas: list[str], inputs: dict[str, str]) -> list[str]: ...


class MotorCrewAI:
    """Monta uma Crew sequencial com as tarefas pedidas e devolve a saída de cada uma."""

    def __init__(self, modelo: str = MODELO, base_url: str = BASE_URL) -> None:
        self.modelo, self.base_url = modelo, base_url
        self._llm = None

    def _criar_llm(self):
        from crewai import LLM
        if self._llm is None:
            self._llm = LLM(model=self.modelo, base_url=self.base_url, is_litellm=True,
                            temperature=0.3, timeout=300, max_tokens=1200,
                            num_ctx=NUM_CTX)
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
                agentes[nome] = Agent(
                    role=a["role"], goal=a["goal"],
                    backstory=a["backstory"] + "\n\n" + REGRAS,
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
