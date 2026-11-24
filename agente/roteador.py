"""Roteador de intenção.

Primeiro regras determinísticas (rápidas, testáveis, seguras). Só quando nada casa
é que o tutor pergunta ao agente Roteador (LLM) qual é a intenção.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Callable

from .conhecimento import GOF_FORA, PADROES, Padrao
from .estado import EstadoAluno

INTENCOES = (
    "contexto", "problema", "conceito", "participantes", "mecanismo", "custos", "quando", "confusoes", "erro",
    "exemplo", "fechamento", "comparar", "exercicio", "avaliacao", "abandonar_exercicio",
    "continuar", "duvida",
)

MSG_VAZIO = ("Não recebi nenhuma pergunta. Escreva sua dúvida sobre Strategy ou Adapter, "
             "ou peça um exercício.")
MSG_INVENCAO = ("Não vou inventar um padrão que não existe: isso ensinaria algo falso. Os "
                "padrões que cubro são Strategy e Adapter, ambos do catálogo GoF. Quer "
                "começar por um deles ou comparar os dois?")
MSG_SOLUCAO = ("Não vou entregar a solução pronta: o exercício existe para você treinar o "
               "raciocínio de projeto. Posso dar uma pista, explicar o conceito que está "
               "travando ou corrigir a sua tentativa. Qual dessas ajuda mais?")
MSG_SAUDACAO = ("Olá! Sou um tutor de padrões de projeto e cubro Strategy e Adapter. Podemos "
                "começar pelo problema que cada um resolve, ver um exemplo em Java ou "
                "partir direto para um exercício. Por qual quer começar?")
MSG_QUAL_PADRAO = ("Consigo ensinar Strategy e Adapter, mas não ficou claro qual deles você "
                   "quer. Pode citar o nome do padrão?")
MSG_FORA_TOPICO = ("Não sei responder a isso: meu material cobre apenas Strategy e Adapter, "
                   "do catálogo GoF. Posso explicar um dos dois, mostrar um exemplo, propor "
                   "um exercício ou corrigir sua tentativa. Qual desses ajuda?")


def msg_fora_escopo(nome: str) -> str:
    return (f"{nome.title()} é do catálogo GoF, mas este tutor cobre apenas Strategy e "
            "Adapter, e prefiro não improvisar sobre o que não está no meu material. "
            "Para esse padrão, consulte o material da disciplina. Quer voltar a Strategy "
            "ou Adapter?")


@dataclass
class Decisao:
    intencao: str | None = None
    padrao: Padrao | None = None
    resposta: str | None = None   # resposta fixa (fallback ou recusa)
    motivo: str = ""
    conversa: bool = False        # True: o tutor reformula a resposta com o modelo
    alvo: str = ""                # padrão fora de escopo citado


def norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower().strip()


def _tem(texto_norm: str, termos: tuple[str, ...]) -> bool:
    return any(t in texto_norm for t in termos)


def _palavra(texto_norm: str, termo: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(termo)}(?!\w)", texto_norm) is not None


def _saudacao(texto_norm: str) -> bool:
    """Reconhece saudação mesmo com pontuação no fim."""
    return texto_norm.strip(" !?.,;:") in SAUDACOES


PALAVRAS_EXERCICIO = ("exercicio", "praticar", "pratica", "me testa", "desafio",
                      "treinar", "quiz", "teste")
PALAVRAS_EXPLICACAO = ("explique", "explica", "o que e", "como funciona", "para que serve",
                       "diferenca", "quando usar", "quando evitar", "defina", "conceito")

PALAVRAS_POR_INTENCAO: dict[str, tuple[str, ...]] = {
    "exemplo": ("exemplo", "codigo", "java", "implementa", "mostre"),
    "participantes": ("participante", "estrutura", "uml", "diagrama", "papeis",
                      "quem sao", "classes envolvidas"),
    "mecanismo": ("como funciona", "mecanismo", "por baixo", "por que funciona",
                  "polimorfismo", "funciona por"),
    "custos": ("custo", "desvantagem", "vantagem", "preco", "consequencia", "trade",
               "o que se perde", "contras"),
    "quando": ("quando usar", "quando evitar", "quando nao", "devo usar", "vale a pena",
               "exagero", "evitar", "quando aplicar", "melhor escolha",
               "deve ser evitado", "deve ser evitada", "situacao em que",
               "situacoes em que", "evitado", "evitada"),
    "confusoes": ("confund", "diferenca", "parecid", "versus", " vs ", " x ",
                  "qual a diferenca"),
    "erro": ("erro", "errado", "errada", "equivoc", "incorret", "armadilha", "ma pratica",
             "corrigir", "correcao", "uso indevido", "mal uso"),
    "fechamento": ("lembrar", "resumo", "resumir", "fechamento", "antes de usar",
                   "checklist", "revisao"),
    "contexto": ("padrao de projeto", "design pattern", "gof", "gang of four", "catalogo",
                 "por que e um padrao", "categoria", "familia"),
    "problema": ("problema", "para que serve", "resolve", "por que existe", "motivacao"),
    "conceito": ("o que e", "explique", "explica", "defina", "conceito", "comecar",
                 "introducao", "aprender"),
}
ORDEM_DESEMPATE = ("exemplo", "participantes", "mecanismo", "custos", "quando",
                   "confusoes", "erro", "fechamento", "contexto", "problema", "conceito")

SAUDACOES = {"oi", "ola", "bom dia", "boa tarde", "boa noite", "e ai", "hello", "hi"}
ABANDONAR = ("outro topico", "outro assunto", "outra pergunta", "deixa o exercicio",
             "deixa pra la", "deixa para la", "nao quero o exercicio", "nao quero fazer",
             "pula o exercicio", "pular o exercicio", "cancela o exercicio",
             "muda de assunto", "quero outro topico", "quero outro assunto")
SINAIS_RESPOSTA = ("eu ", "faria", "criaria", "usaria", "colocaria", "implementaria",
                   "seria", "acho", "penso", "resposta", "porque", "pois", "assim",
                   "interface", "classe", "delegaria", "injetaria", "separaria")
CONTINUAR = ("sim", "pode", "continue", "continua", "vamos", "proximo", "seguir", "claro",
             "quero", "bora", "mais", "aprofunde", "ok", "pode ser")

ESQUECER_ATUAL = ("esquece", "esqueca", "deixa o", "deixa de lado", "so quero", "somente")
PEDIDO_DE_EXPLICACAO = ("fale", "falar", "me fale", "explic", "conte", "descreva",
                        "detalhe", "o que e", "como funciona", "modelo", "saber sobre")
COMPARACAO = ("diferenca", "confund", "parecid", "versus", " vs ", " x ",
              "compar", "qual a diferenca")
# Sinais de que a mensagem é sobre o material, mesmo sem citar o nome do padrão.
CUES_PADRAO = ("padrao", "strategy", "adapter", "estrategia", "adaptador", "gof", "catalogo",
               "exemplo", "exercicio", "aula", "explic", "mecanismo", "participante", "custo",
               "quando", "usar", "evitar", "devo usar", "erro", "diferenca", "confus",
               "contexto", "java", "interface", "classe", "heranca", "composicao",
               "polimorfismo", "context", "target", "adaptee", "codigo", "topico", "tema",
               "conceito", "mini-aula")
# Reações curtas de conversa podem seguir para o classificador; assunto alheio, não.
CUES_CONVERSA = ("isso", "agora", "entao", "legal", "interessante", "hmm", "ok", "pois",
                 "faz sentido", "continua", "continue", "pode", "sim")


def padroes_no_texto(texto: str) -> list[Padrao]:
    t = norm(texto)
    return [p for p in PADROES.values() if any(k in t for k in p.palavras_chave)]


def _outros_gof(texto: str) -> list[str]:
    t = norm(texto)
    return [n for n in GOF_FORA if _palavra(t, n)]


def _fora_do_tema(t: str, citados: list[Padrao]) -> bool:
    """Bloqueia assunto alheio antes de chamar o classificador.

    Uma pergunta sobre o material pode não citar o nome do padrão, então usamos
    sinais do vocabulário do tutor. Reações curtas de conversa continuam livres
    para o LLM decidir; o que não tem relação nenhuma é recusado sem gasto.
    """
    if citados or _tem(t, CUES_PADRAO) or _tem(t, CUES_CONVERSA):
        return False
    return len(t) >= 30 or "?" in t


def quer_invencao(texto: str) -> bool:
    t = norm(texto)
    if _tem(t, ("nao invente", "não invente", "nao inventa", "não inventa",
                "sem inventar", "nao invencao", "não invenção")):
        return False
    return "invent" in t or ("padrao" in t and _tem(t, ("ficticio", "imaginario", "que nao existe")))


def quer_solucao_pronta(texto: str) -> bool:
    t = norm(texto)
    if "exemplo" in t or "explique" in t:
        return False
    return _tem(t, ("solucao completa", "solucao pronta", "resposta pronta", "codigo pronto",
                    "resolva para mim", "resolva pra mim", "faca por mim", "gabarito",
                    "me de a resposta", "me entregue a resposta", "entregue o codigo"))


def quer_exercicio(texto: str) -> bool:
    t = norm(texto)
    return any(_palavra(t, p) for p in PALAVRAS_EXERCICIO)


def _quer_explicacao(texto: str) -> bool:
    t = norm(texto)
    return _tem(t, PALAVRAS_EXPLICACAO)


def parece_resposta_ao_exercicio(texto: str, estado: EstadoAluno) -> bool:
    if not estado.exercicio:
        return False
    t = norm(texto)
    if "minha resposta" in t:
        return True
    if quer_exercicio(texto) or _quer_explicacao(texto) or "?" in t:
        return False
    if _saudacao(t):
        return False
    return _tem(t, SINAIS_RESPOSTA)


def _intencao_por_qualificador(t: str) -> str | None:
    """O que qualifica o pedido vence palavras genéricas como "exemplo".

    "exemplo de quando usar" pede seleção, não um exemplo; "exemplo de uso
    equivocado" pede o erro comum, não um exemplo de aplicação.
    """
    if re.search(r"\bexemplo de (?:um )?(?:erro|uso (?:errado|equivocado|incorreto|"
                 r"indevido)|aplicacao (?:errada|equivocada|incorreta|indevida))", t):
        return "erro"
    if re.search(r"\bexemplo de (?:quando|situacao|situacoes|melhor escolha)", t):
        return "quando"
    if re.search(r"\b(?:explique|explica|defina)\b.*\b(?:problema|resolve|util)\b", t):
        return "conceito"
    return None


def _pontuar(t: str) -> str | None:
    placar = {i: sum(1 for k in ks if k in t) for i, ks in PALAVRAS_POR_INTENCAO.items()}
    melhor = max(placar.values())
    if melhor == 0:
        return None
    for i in ORDEM_DESEMPATE:
        if placar[i] == melhor:
            return i
    return None


def _proximo(padrao: Padrao, estado: EstadoAluno) -> str | None:
    vistos = estado.ja_viu(padrao.nome)
    return next((t for t in padrao.progressao if t not in vistos), None)


def proximo_topico(padrao: Padrao, estado: EstadoAluno) -> str | None:
    return _proximo(padrao, estado)


def rotear(
    texto: str,
    estado: EstadoAluno,
    classificador: Callable[[str, Padrao | None], str | None] | None = None,
) -> Decisao:
    texto = (texto or "").strip()
    if not texto:
        return Decisao(resposta=MSG_VAZIO, motivo="vazio")
    t = norm(texto)

    if quer_invencao(texto):
        return Decisao(resposta=MSG_INVENCAO, motivo="invencao")
    if quer_solucao_pronta(texto):
        return Decisao(resposta=MSG_SOLUCAO, motivo="solucao_pronta")

    atual = PADROES.get((estado.padrao or "").lower())
    citados = padroes_no_texto(texto)

    # "esquece o adapter..." não pode continuar usando o padrão da sessão
    if _tem(t, ESQUECER_ATUAL):
        atual = None
        nome_atual = (estado.padrao or "").lower()
        citados = [p for p in citados if p.nome.lower() != nome_atual]

    # abandono explícito de um exercício pendente
    if estado.exercicio and _tem(t, ABANDONAR):
        return Decisao("abandonar_exercicio", atual, motivo="abandona_exercicio")

    # resposta a um exercício pendente (o padrão é o do exercício)
    if parece_resposta_ao_exercicio(texto, estado):
        p = PADROES.get((estado.exercicio_padrao or "").lower()) or atual
        if p:
            return Decisao("avaliacao", p, motivo="resposta_exercicio")

    if _saudacao(t):
        return Decisao(resposta=MSG_SAUDACAO, motivo="saudacao", conversa=True)

    # padrão-alvo da mensagem
    if len(citados) > 1:
        return Decisao("comparar", None, motivo="dois_padroes")
    padrao = citados[0] if citados else atual

    # padrão GoF citado que o tutor não cobre
    outros = _outros_gof(texto)
    if outros:
        comparando = _tem(t, COMPARACAO) or t.startswith(("e o ", "e a "))
        base = citados or ([atual] if atual else [])
        if comparando:
            vizinhos = {norm(v) for p in base for v in p.vizinhos()}
            fora = [n for n in outros if norm(n) not in vizinhos]
        else:
            # "fale sobre Bridge" pede explicação, não comparação: recusa mesmo
            # quando o padrão é vizinho do que está em estudo.
            fora = list(outros)
        if fora:
            return Decisao(resposta=msg_fora_escopo(fora[0]), motivo="fora_escopo",
                           conversa=True, alvo=fora[0])
        if base and comparando:
            return Decisao("confusoes", base[0], motivo="vizinho")

    if _fora_do_tema(t, citados):
        return Decisao(resposta=MSG_FORA_TOPICO, motivo="fora_topico")

    if padrao is None:
        return Decisao(resposta=MSG_QUAL_PADRAO, motivo="sem_padrao", conversa=True)

    # pedido de exercício
    if quer_exercicio(texto) and not _quer_explicacao(texto):
        return Decisao("exercicio", padrao, motivo="pede_exercicio")

    # "sim / continue": segue a progressão do padrão
    if (len(t) <= 25 and t.strip("!. ") in CONTINUAR) or t.startswith(("continu", "prossig", "segue")):
        prox = _proximo(padrao, estado)
        return Decisao(prox or "exercicio", padrao, motivo="continuar")

    intencao = _intencao_por_qualificador(t) or _pontuar(t)
    if intencao == "conceito" and not estado.ja_viu(padrao.nome):
        intencao = "contexto"   # primeiro contato: começa pelo contexto
    if intencao:
        return Decisao(intencao, padrao, motivo="palavras_chave")

    # nada casou: pergunta ao agente Roteador, se houver
    if classificador:
        rotulo = classificador(texto, padrao)
        if rotulo in INTENCOES and rotulo not in ("avaliacao", "continuar"):
            return Decisao(rotulo, padrao, motivo="llm")
    return Decisao("duvida", padrao, motivo="indefinido")
