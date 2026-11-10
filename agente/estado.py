"""Estado do aluno: memória estruturada além do texto da conversa."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EstadoAluno:
    padrao: str | None = None                       # padrão em estudo
    vistos: dict[str, list[str]] = field(default_factory=dict)  # padrão -> tópicos já vistos
    dificuldades: list[str] = field(default_factory=list)       # conceitos errados/incompletos
    exercicio: str | None = None                    # exercício pendente (texto integral)
    exercicio_padrao: str | None = None
    tentativas: int = 0
    acertos: int = 0
    mensagens: list[tuple[str, str]] = field(default_factory=list)

    def registrar(self, papel: str, texto: str) -> None:
        self.mensagens.append((papel, texto))

    def marcar_visto(self, padrao: str, topico: str) -> None:
        lista = self.vistos.setdefault(padrao, [])
        if topico not in lista:
            lista.append(topico)

    def ja_viu(self, padrao: str) -> list[str]:
        return list(self.vistos.get(padrao, []))

    def registrar_dificuldade(self, texto: str) -> None:
        texto = texto.strip()
        if texto and texto not in self.dificuldades:
            self.dificuldades.append(texto)
            self.dificuldades = self.dificuldades[-4:]

    def historico_curto(self, n: int = 6) -> str:
        """Últimas mensagens; falas longas do sistema viram só o começo."""
        if not self.mensagens:
            return "(início da conversa)"
        linhas = []
        for papel, texto in self.mensagens[-n:]:
            limite = 400 if papel == "estudante" else 280
            texto = " ".join(texto.split())
            if len(texto) > limite:
                corte = texto[:limite].rsplit(" ", 1)[0] or texto[:limite]
                texto = corte + "..."
            linhas.append(f"{papel}: {texto}")
        return "\n".join(linhas)

    def resumo(self, nome_padrao: str, proximo: str | None) -> str:
        vistos = self.ja_viu(nome_padrao)
        partes = [
            f"Padrão em estudo: {nome_padrao}.",
            "Já abordado: " + (", ".join(vistos) if vistos else "nada ainda") + ".",
            "Exercício pendente: " + ("sim" if self.exercicio else "não") + ".",
        ]
        if self.dificuldades:
            partes.append("Dificuldades observadas: " + "; ".join(self.dificuldades) + ".")
        if self.tentativas:
            partes.append(f"Exercícios respondidos: {self.tentativas} (corretos: {self.acertos}).")
        partes.append("Apoio: " + ("reduza as dicas, o aluno já acertou um exercício."
                                   if self.acertos else "alto, o aluno ainda está começando."))
        if proximo:
            partes.append(f"Próximo tópico sugerido: {proximo}.")
        return " ".join(partes)
