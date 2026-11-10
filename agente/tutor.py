"""Orquestração do tutor: roteia, ensina, revisa (e corrige) e atualiza o estado."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path

from .conhecimento import (DESCRICAO_INTENCAO, PADROES, TOPICOS_POR_INTENCAO, Padrao,
                           fatos_comparacao, renderizar_fatos)
from .estado import EstadoAluno
from .motor import MODELO, Motor, MotorCrewAI
from .prompts import INSTRUCOES_INTENCAO
from .roteador import Decisao, proximo_topico, rotear
from .validadores import (extrair_resultado, extrair_veredito, palavras, validar_exemplo,
                          validar_exercicio, validar_feedback, validar_texto,
                          veredito_efetivo)

DIR_EVIDENCIAS = Path(__file__).resolve().parent.parent / "evidencias"
LIMITES = {"contexto": 130, "conceito": 110, "problema": 140, "comparar": 200,
           "fechamento": 150}
LIMITE_PADRAO = 120
MAX_TENTATIVAS = 2

MSG_ERRO_MODELO = ("Não consegui falar com o modelo local agora. Verifique se o Ollama está "
                   "rodando (comando: ollama ps) e tente de novo.")


def _limpar(texto: str) -> str:
    texto = (texto or "").strip()
    texto = re.sub(r"^(resposta|explicação|mini-aula)\s*:\s*", "", texto, flags=re.IGNORECASE)
    return texto.strip()


def _sem_codigo(texto: str) -> str:
    texto = re.sub(r"```.*?```", "", texto, flags=re.DOTALL)
    return texto.split("```")[0].strip()


class Tutor:
    def __init__(self, motor: Motor | None = None, registrar: bool = True) -> None:
        self.motor: Motor = motor or MotorCrewAI()
        self.estado = EstadoAluno()
        self.registrar = registrar

    def reiniciar(self) -> None:
        self.estado = EstadoAluno()

    # ------------------------------------------------------------------ API
    def responder(self, texto: str) -> str:
        texto = (texto or "").strip()
        inicio = time.perf_counter()
        info: dict = {"tentativas": 0, "fallback": False}
        try:
            decisao = rotear(texto, self.estado, self._classificar_com_llm)
            if decisao.resposta is not None:
                resposta = (self._conversar(decisao, texto, info) if decisao.conversa
                            else decisao.resposta)
            else:
                resposta = self._executar(decisao, texto, info)
        except Exception as erro:  # falha do modelo ou saída inesperada
            info["erro"] = type(erro).__name__
            return f"{MSG_ERRO_MODELO}\nDetalhe técnico: {type(erro).__name__}"
        if texto:
            self.estado.registrar("estudante", texto)
            self.estado.registrar("sistema", resposta)
        if self.registrar:
            self._log(decisao, texto, time.perf_counter() - inicio, info)
        return resposta

    # ------------------------------------------------------------- roteamento
    def _classificar_com_llm(self, texto: str, padrao: Padrao | None) -> str | None:
        try:
            saida = self.motor.rodar(["roteador"], {
                "pergunta": texto, "padrao_nome": padrao.nome if padrao else "nenhum"})
            return re.sub(r"[^a-z]", "", (saida[0] or "").lower().split()[0]) if saida and saida[0].strip() else None
        except Exception:
            return None

    def _executar(self, d: Decisao, texto: str, info: dict) -> str:
        i = d.intencao
        if i == "abandonar_exercicio":
            return self._abandonar_exercicio(d.padrao)
        if i == "exercicio":
            return self._exercicio(d.padrao, info)
        if i == "avaliacao":
            return self._avaliacao(d.padrao, texto, info)
        if i == "exemplo":
            return self._exemplo(d.padrao, texto, info)
        return self._explicar(d, texto, info)

    def _abandonar_exercicio(self, p: Padrao | None) -> str:
        self.estado.exercicio = None
        self.estado.exercicio_padrao = None
        if p is None:
            return ("Tudo bem, deixei o exercício pendente de lado. Quer continuar em "
                    "Strategy ou Adapter?")
        prox = proximo_topico(p, self.estado)
        sugestao = (f"Podemos seguir para {prox}." if prox
                    else "Quer tentar outro exercício ou rever um tópico?")
        return (f"Tudo bem, deixei o exercício pendente de lado. Continuamos em {p.nome}. "
                f"{sugestao}")

    # ------------------------------------------------- produção com guardião
    def _produzir(self, produtor: str, guardiao: str, inputs: dict, validar,
                  info: dict, fallback, pos=_limpar) -> str:
        """Gera, valida (regras + guardião) e, se falhar, regenera uma vez; depois usa o fallback."""
        correcao = ""
        for tentativa in range(1, MAX_TENTATIVAS + 1):
            info["tentativas"] = tentativa
            saidas = self.motor.rodar([produtor, guardiao], {**inputs, "correcao": correcao})
            texto = pos(_limpar(saidas[0]))
            veredito, motivo = extrair_veredito(saidas[1] if len(saidas) > 1 else "")
            veredito = veredito_efetivo(veredito, motivo)
            problemas = validar(texto)
            info["parecer"] = f"{veredito}: {motivo}"
            if not problemas and veredito != "CORRIGIR":
                return texto
            partes = problemas + ([motivo] if veredito == "CORRIGIR" and motivo else [])
            correcao = ("CORREÇÃO OBRIGATÓRIA: a versão anterior foi rejeitada ("
                        + "; ".join(partes) + "). Refaça corrigindo isso.")
            info["problemas"] = partes
        info["fallback"] = True
        return fallback()

    # ---------------------------------------------------------------- conversa
    _INSTRUCAO_CONVERSA = {
        "saudacao": "Cumprimente de volta, apresente-se em uma frase (tutor de Strategy e "
                    "Adapter) e pergunte, de forma simples, o que o aluno já conhece ou por "
                    "onde quer começar.",
        "sem_padrao": "Não ficou claro de qual padrão o aluno fala. Use a CONVERSA RECENTE; "
                      "se for um pedido como 'continue', pergunte com naturalidade sobre qual "
                      "dos dois padrões ele quer seguir e ofereça um ponto de partida.",
        "fora_escopo": "O aluno citou um padrão que este tutor não cobre ({alvo}). Diga com "
                       "honestidade, em 1 ou 2 frases, que não faz parte do material e que "
                       "você não vai improvisar. NÃO explique esse padrão. Sugira o material "
                       "da disciplina e ofereça Strategy ou Adapter.",
    }

    def _conversar(self, d: Decisao, texto: str, info: dict) -> str:
        """Respostas curtas de conversa pelo modelo; se falhar, usa a mensagem fixa."""
        instrucao = self._INSTRUCAO_CONVERSA.get(d.motivo)
        if not instrucao:
            return d.resposta or ""
        cobertura = ("COBERTURA DO TUTOR: padrões Strategy (comportamental) e Adapter "
                     "(estrutural), ambos do catálogo GoF.\nStrategy: "
                     + PADROES["strategy"].definicao + "\nAdapter: "
                     + PADROES["adapter"].definicao)
        limite = 70
        inputs = {
            "fatos": cobertura, "estado": self.estado.resumo(self.estado.padrao or "nenhum", None),
            "historico": self.estado.historico_curto(), "pergunta": texto,
            "instrucao": instrucao.format(alvo=d.alvo), "padrao_nome": "Strategy e Adapter",
            "estrategia": "Seja caloroso e breve.", "abertura": "", "limite": str(limite),
            "pergunta_final": "uma pergunta simples para saber por onde começar",
        }
        try:
            info["tentativas"] = 1
            saidas = self.motor.rodar(["tutor"], inputs)
            txt = _sem_codigo(_limpar(saidas[0]))
            if txt and palavras(txt) <= int(limite * 1.6):
                return txt
        except Exception as erro:
            info["erro"] = type(erro).__name__
        info["fallback"] = True
        return d.resposta or ""

    # --------------------------------------------------------------- explicar
    def _explicar(self, d: Decisao, texto: str, info: dict) -> str:
        i = d.intencao
        if i == "comparar":
            p, fatos, nome, confusao = PADROES["strategy"], fatos_comparacao(), "Strategy e Adapter", "Adapter"
            topico = None
        else:
            p = d.padrao
            if i == "continuar":
                i = "conceito"
            fatos = p.fatos(TOPICOS_POR_INTENCAO.get(i, TOPICOS_POR_INTENCAO["duvida"]))
            nome, topico = p.nome, (i if i in DESCRICAO_INTENCAO else None)

        vistos = self.estado.ja_viu(p.nome)
        if i == "comparar":
            abertura = "Se o aluno já viu algum dos padrões, aproveite isso."
        elif i == "problema":
            abertura = f"Narre o problema a partir desta situação: {p.gancho}"
        elif not vistos:
            abertura = (f"É o primeiro contato do aluno com {nome}: seja acolhedor, vá "
                        "devagar e não faça perguntas difíceis.")
        else:
            abertura = ("O aluno já viu: " + ", ".join(vistos) + ". Não repita o que já foi "
                        "explicado; conecte a resposta com isso.")
        proximo = proximo_topico(p, self.estado)
        limite = LIMITES.get(i, LIMITE_PADRAO)
        inputs = {
            "fatos": fatos, "estado": self.estado.resumo(p.nome, proximo),
            "historico": self.estado.historico_curto(), "pergunta": texto,
            "instrucao": INSTRUCOES_INTENCAO.get(i, INSTRUCOES_INTENCAO["duvida"]),
            "padrao_nome": nome, "estrategia": p.estrategia, "abertura": abertura,
            "limite": str(limite), "pergunta_final": p.pergunta_final(i),
            "extra": "a distinção com padrões vizinhos, se houver, está correta e não há 'Context' em Adapter nem 'Adaptee' em Strategy.",
        }
        resposta = self._produzir(
            "tutor", "guardiao_texto", inputs,
            lambda t: validar_texto(t, p, i, limite), info,
            lambda: (fatos_comparacao() + "\n\nQuer ver o sinal prático para distinguir os dois?"
                     if i == "comparar"
                     else renderizar_fatos(p, i if i in TOPICOS_POR_INTENCAO else "conceito")),
            pos=_sem_codigo)
        if "?" not in resposta[-200:]:
            resposta += "\n\n" + p.pergunta_final(i)
        if topico:
            self.estado.marcar_visto(p.nome, topico)
        if i != "comparar":
            self.estado.padrao = p.nome
        return resposta

    # ----------------------------------------------------------------- exemplo
    def _exemplo(self, p: Padrao, texto: str, info: dict) -> str:
        inputs = {
            "codigo": p.exemplo_java, "fatos": p.fatos(("participantes", "mecanismo")),
            "pergunta": texto, "padrao_nome": p.nome,
            "extra": "os comentários descrevem fielmente o código verificado, sem classes inventadas.",
        }
        comentario = self._produzir(
            "exemplificador", "guardiao_texto", inputs, validar_exemplo, info,
            lambda: f"**O que observar:** {p.o_que_observar}\n\n**Se amanhã...:** {p.se_amanha}",
            pos=_sem_codigo)
        resposta = (f"Aqui está um exemplo completo de {p.nome} em Java (arquivo Main.java):\n\n"
                    f"```java\n{p.exemplo_java.strip()}\n```\n\n"
                    f"Estrutura:\n```\n{p.uml}\n```\n\n{comentario}\n\n{p.pergunta_final('exemplo')}")
        self.estado.marcar_visto(p.nome, "exemplo")
        self.estado.padrao = p.nome
        return resposta

    # --------------------------------------------------------------- exercício
    def _exercicio(self, p: Padrao, info: dict) -> str:
        inputs = {
            "fatos": p.fatos(("definicao", "participantes", "erro")),
            "estado": self.estado.resumo(p.nome, None), "dominio": p.dominio_exercicio,
            "padrao_nome": p.nome,
        }
        resposta = self._produzir(
            "exercicio", "guardiao_exercicio", inputs,
            lambda t: validar_exercicio(t, p), info, lambda: p.exercicio_fixo)
        resposta = _sem_codigo(resposta)
        self.estado.exercicio, self.estado.exercicio_padrao = resposta, p.nome
        self.estado.padrao = p.nome
        return resposta

    # --------------------------------------------------------------- avaliação
    def _avaliacao(self, p: Padrao, texto: str, info: dict) -> str:
        inputs = {
            "fatos": p.fatos(("definicao", "participantes", "mecanismo", "evitar", "erro")),
            "exercicio": self.estado.exercicio or "", "pergunta": texto,
            "padrao_nome": p.nome,
        }
        resultado_info: dict = {}

        def validar(t: str) -> list[str]:
            _, res, conc = extrair_resultado(t)
            resultado_info.update(res=res, conc=conc)
            return validar_feedback(t, exigir_resultado=True)

        bruto = self._produzir(
            "avaliacao", "guardiao_feedback", inputs, validar, info,
            lambda: self._feedback_fixo(texto))
        feedback, res, conc = extrair_resultado(bruto)
        if info.get("fallback"):
            res, conc = "PARCIAL", ""
        feedback = _sem_codigo(feedback)

        self.estado.tentativas += 1
        if res == "CORRETO":
            self.estado.acertos += 1
            self.estado.exercicio = None
            feedback += "\n\nQuer um novo exercício ou prefere ver outro tópico?"
        elif conc:
            self.estado.registrar_dificuldade(conc)
        self.estado.padrao = p.nome
        return feedback

    @staticmethod
    def _feedback_fixo(texto: str) -> str:
        trecho = " ".join(texto.split()[:30])
        return (f'**O que você escreveu:** "{trecho}"\n\n'
                "Não consegui avaliar com segurança agora. Confira sua resposta contra os "
                "critérios de sucesso do exercício, um por um, e me diga qual deles você "
                "acha que ainda não cumpriu.\n\n"
                "**Pergunta para avançar:** qual critério foi o mais difícil de atender, e por quê?")

    # ------------------------------------------------------------------ log
    def _log(self, d: Decisao, pergunta: str, duracao: float, info: dict) -> None:
        try:
            DIR_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
            reg = {
                "data_hora": datetime.now().astimezone().isoformat(timespec="seconds"),
                "intencao": d.intencao or d.motivo, "motivo_rota": d.motivo,
                "padrao": d.padrao.nome if d.padrao else None, "pergunta": pergunta,
                "duracao_s": round(duracao, 1), "modelo": MODELO, **info,
            }
            with (DIR_EVIDENCIAS / "execucoes.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(reg, ensure_ascii=False) + "\n")
        except OSError:
            pass
