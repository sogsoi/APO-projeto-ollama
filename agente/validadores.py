"""Validações determinísticas (não dependem do modelo)."""

from __future__ import annotations

import re

from .conhecimento import Padrao


def contem_termo(texto: str, termo: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(termo)}(?!\w)", texto, flags=re.IGNORECASE) is not None


def palavras(texto: str) -> int:
    return len(texto.split())


def tem_bloco_codigo(texto: str) -> bool:
    return "```" in texto


def validar_texto(texto: str, padrao: Padrao, intencao: str, limite: int) -> list[str]:
    problemas = []
    if not texto.strip():
        problemas.append("resposta vazia")
    if tem_bloco_codigo(texto):
        problemas.append("não escreva código Java; o exemplo é exibido pelo sistema")
    if palavras(texto) > int(limite * 1.7):
        problemas.append(f"texto longo demais (máximo {limite} palavras)")
    if intencao not in ("comparar", "confusoes", "duvida"):
        for termo in padrao.termos_invalidos:
            if contem_termo(texto, termo):
                problemas.append(f"'{termo}' não faz parte do padrão {padrao.nome}")
    return problemas


def validar_exemplo(texto: str) -> list[str]:
    problemas = []
    if not texto.strip():
        problemas.append("resposta vazia")
    if tem_bloco_codigo(texto):
        problemas.append("não escreva código; só os comentários")
    return problemas


def validar_exercicio(texto: str, padrao: Padrao) -> list[str]:
    problemas = []
    if not texto.strip():
        return ["resposta vazia"]
    if tem_bloco_codigo(texto):
        problemas.append("exercício não pode conter código")
    for termo in padrao.termos_proibidos_exercicio:
        if contem_termo(texto, termo):
            problemas.append(f"o exercício revela o termo '{termo}'")
    for marca in ("**Cenário:**", "**Sua tarefa:**", "Minha resposta"):
        if marca not in texto:
            problemas.append(f"falta a seção '{marca}'")
    if palavras(texto) > 300:
        problemas.append("exercício longo demais")
    return problemas


def validar_feedback(texto: str, exigir_resultado: bool = False) -> list[str]:
    problemas = []
    if not texto.strip():
        return ["resposta vazia"]
    if tem_bloco_codigo(texto):
        problemas.append("feedback não pode conter código")
    if "Pergunta para avançar" not in texto:
        problemas.append("falta a 'Pergunta para avançar'")
    if exigir_resultado:
        if not re.search(r"RESULTADO:\s*(CORRETO|PARCIAL|INCORRETO)", texto, re.IGNORECASE):
            problemas.append("falta a linha 'RESULTADO: CORRETO|PARCIAL|INCORRETO'")
        if not re.search(r"CONCEITO:\s*\S+", texto, re.IGNORECASE):
            problemas.append("falta a linha 'CONCEITO: ...'")
    return problemas


def extrair_veredito(texto: str) -> tuple[str, str]:
    """('OK'|'CORRIGIR'|'INDEFINIDO', motivo)."""
    marcas = list(re.finditer(r"VEREDITO:\s*(OK|CORRIGIR)\b", texto or "", flags=re.IGNORECASE))
    if not marcas:
        return "INDEFINIDO", (texto or "").strip()[:200]
    m = marcas[-1]
    motivo = re.sub(r"\s+", " ", texto[: m.start()].replace("**", "")).strip(" -:\n")
    return m.group(1).upper(), motivo[:300]


_OMISSAO = ("falt", "nao menciona", "não menciona", "nao mencionou", "não mencionou",
            "omit", "lacuna", "poderia mencionar", "incompleto")
_ERRO = ("erro", "incorret", "invent", "contradiz", "contradição", "errad", "falso",
         "confunde", "outro padrão", "outro padrao")


def veredito_efetivo(veredito: str, motivo: str) -> str:
    """Lacuna/omissão não é erro: o texto é curto de propósito."""
    if veredito != "CORRIGIR":
        return veredito
    m = re.sub(r"\b(não|nao|sem|nenhum|nenhuma)\s+\w+", " ", motivo.lower())  # ignora negações
    if any(k in m for k in _OMISSAO) and not any(k in m for k in _ERRO):
        return "OK"
    return veredito


def extrair_resultado(texto: str) -> tuple[str, str, str]:
    """Separa as linhas RESULTADO/CONCEITO do feedback. Devolve (texto_limpo, resultado, conceito)."""
    resultado, conceito = "PARCIAL", ""
    m = re.search(r"RESULTADO:\s*(CORRETO|PARCIAL|INCORRETO)", texto, flags=re.IGNORECASE)
    if m:
        resultado = m.group(1).upper()
    c = re.search(r"CONCEITO:\s*(.+)", texto, flags=re.IGNORECASE)
    if c:
        conceito = c.group(1).strip(" *.")
    limpo = re.sub(r"^\s*\**(RESULTADO|CONCEITO)\**\s*:.*$", "", texto,
                   flags=re.IGNORECASE | re.MULTILINE).strip()
    return limpo, resultado, conceito
