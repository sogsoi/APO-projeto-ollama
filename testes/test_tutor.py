"""Testes que não chamam o modelo (motor falso)."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from agente.conhecimento import ADAPTER, PADROES, STRATEGY
from agente.estado import EstadoAluno
from agente.roteador import rotear
from agente.tutor import Tutor
from agente.validadores import (extrair_resultado, extrair_veredito, validar_exercicio,
                                validar_feedback, validar_texto)


class MotorFalso:
    """Devolve saídas roteirizadas, uma lista por chamada."""
    def __init__(self, *chamadas, erro=None):
        self.chamadas, self.erro, self.recebidos = list(chamadas), erro, []

    def rodar(self, tarefas, inputs):
        self.recebidos.append((tarefas, inputs))
        if self.erro:
            raise self.erro
        return self.chamadas.pop(0)


def estado_com_exercicio(padrao="Strategy"):
    e = EstadoAluno(padrao=padrao)
    e.exercicio, e.exercicio_padrao = "**Cenário:** x", padrao
    return e


class RoteadorTest(unittest.TestCase):
    def setUp(self): self.e = EstadoAluno()

    def test_vazio(self): self.assertEqual(rotear("  ", self.e).motivo, "vazio")
    def test_invencao(self): self.assertEqual(rotear("Invente um padrão chamado Z", self.e).motivo, "invencao")
    def test_solucao(self): self.assertEqual(rotear("Me entregue o código pronto de uma solução completa", self.e).motivo, "solucao_pronta")
    def test_primeiro_contato_comeca_pelo_contexto(self): self.assertEqual(rotear("Explique o que é o Strategy", self.e).intencao, "contexto")
    def test_depois_do_contexto_vem_conceito(self):
        self.e.marcar_visto("Strategy", "contexto")
        self.assertEqual(rotear("Explique o que é o Strategy", self.e).intencao, "conceito")
    def test_problema(self): self.assertEqual(rotear("Que problema o Strategy resolve?", self.e).intencao, "problema")
    def test_continue_sem_acento(self): self.assertEqual(rotear("Continue a explicacao", EstadoAluno(padrao="Strategy")).motivo, "continuar")
    def test_exemplo(self): self.assertEqual(rotear("Dê um exemplo de Adapter em Java", self.e).intencao, "exemplo")
    def test_quando(self): self.assertEqual(rotear("Quando devo evitar o Strategy?", self.e).intencao, "quando")
    def test_comparar(self): self.assertEqual(rotear("Qual a diferença entre Strategy e Adapter?", self.e).intencao, "comparar")
    def test_exercicio(self): self.assertEqual(rotear("Me dê um exercício sobre Adapter", self.e).intencao, "exercicio")
    def test_sem_padrao(self): self.assertEqual(rotear("quando devo usar?", self.e).motivo, "sem_padrao")

    def test_fora_de_escopo(self):
        d = rotear("Explique o Observer", self.e)
        self.assertEqual(d.motivo, "fora_escopo")
        self.assertIn("Observer", d.resposta)

    def test_vizinho_vira_confusao(self):
        self.e.padrao = "Adapter"
        d = rotear("E o Bridge?", self.e)
        self.assertEqual((d.intencao, d.padrao.nome), ("confusoes", "Adapter"))

    def test_cenario_1_primeiro_contato_comeca_pelo_contexto(self):
        texto = "Explique o padrão Strategy e qual problema ele resolve."
        self.assertEqual(rotear(texto, self.e).intencao, "contexto")
        self.e.marcar_visto("Strategy", "contexto")
        self.assertEqual(rotear(texto, self.e).intencao, "conceito")

    def test_cenario_3_selecao(self):
        texto = ("Descreva uma situação em que o Strategy é a melhor escolha e uma em "
                 "que ele deve ser evitado.")
        self.assertEqual(rotear(texto, self.e).intencao, "quando")

    def test_cenario_4_uso_incorreto(self):
        texto = "Como o Strategy costuma ser aplicado de forma errada? Como corrigir?"
        self.assertEqual(rotear(texto, self.e).intencao, "erro")

    def test_exemplo_de_quando_pede_selecao(self):
        texto = "Dê um exemplo de quando usar o Adapter, explicando o porquê."
        self.assertEqual(rotear(texto, self.e).intencao, "quando")

    def test_exemplo_de_uso_equivocado_pede_erro(self):
        self.assertEqual(rotear("Dê um exemplo de uso equivocado do Strategy.", self.e).intencao, "erro")

    def test_fora_do_escopo_vence_confusao(self):
        d = rotear("Qual a diferença entre Strategy e Observer?", self.e)
        self.assertEqual(d.motivo, "fora_escopo")
        self.assertIn("Observer", d.resposta)

    def test_vizinho_do_padrao_citado_vira_confusao(self):
        d = rotear("Qual a diferença entre Strategy e State?", self.e)
        self.assertEqual((d.intencao, d.padrao.nome), ("confusoes", "Strategy"))

    def test_explicacao_de_vizinho_fora_do_escopo_e_recusada(self):
        estado = EstadoAluno(padrao="Adapter")
        d = rotear("fale sobre o modelo bridge", estado)
        self.assertEqual(d.motivo, "fora_escopo")
        self.assertEqual(d.alvo, "bridge")
        self.assertIn("Bridge", d.resposta)

    def test_esquece_o_padrao_atual_nao_usa_estado_da_sessao(self):
        estado = EstadoAluno(padrao="Adapter")
        d = rotear("esquece o adapter, me fale apenas do proxy", estado)
        self.assertEqual(d.motivo, "fora_escopo")
        self.assertEqual(d.alvo, "proxy")
        self.assertIn("Proxy", d.resposta)

    def _assert_fora_do_tema(self, texto):
        chamadas = []

        def classificador(pergunta, padrao):
            chamadas.append(pergunta)
            return "conceito"

        d = rotear(texto, EstadoAluno(padrao="Adapter"), classificador)
        self.assertEqual(chamadas, [])          # não gasta modelo com assunto alheio
        self.assertIsNone(d.intencao)
        self.assertIsNone(d.padrao)
        self.assertEqual(d.motivo, "fora_topico")
        self.assertIn("Strategy e Adapter", d.resposta)

    def test_ofensiva_nao_vira_conceito_do_padrao_da_sessao(self):
        self._assert_fora_do_tema("voce ja goonou hoje?")

    def test_hardware_nao_vira_conceito_do_padrao_da_sessao(self):
        self._assert_fora_do_tema("quais partes um computador tem como hardware")

    def test_padrao_da_sessao(self):
        self.e.padrao = "Strategy"
        self.assertEqual(rotear("quando devo evitar?", self.e).padrao.nome, "Strategy")

    def test_pergunta_atual_vence_sessao(self):
        self.e.padrao = "Strategy"
        self.assertEqual(rotear("e o Adapter, o que é?", self.e).padrao.nome, "Adapter")

    def test_continuar_segue_progressao(self):
        self.e.padrao = "Adapter"; self.e.marcar_visto("Adapter", "contexto")
        d = rotear("sim", self.e)
        self.assertEqual(d.intencao, "conceito")

    def test_progressoes_diferem(self):
        self.assertNotEqual(STRATEGY.progressao, ADAPTER.progressao)

    def test_resposta_ao_exercicio(self):
        d = rotear("Minha resposta: eu criaria uma interface para as regras", estado_com_exercicio())
        self.assertEqual(d.intencao, "avaliacao")

    def test_pergunta_apos_exercicio_nao_e_avaliacao(self):
        d = rotear("e se eu usar herança?", estado_com_exercicio())
        self.assertNotEqual(d.intencao, "avaliacao")

    def test_fala_longa_sem_sinal_de_resposta_nao_e_avaliacao(self):
        d = rotear("me fale mais sobre o papel do contexto nesse caso", estado_com_exercicio())
        self.assertNotEqual(d.intencao, "avaliacao")
        self.assertNotEqual(d.motivo, "resposta_exercicio")

    def test_abandonar_exercicio(self):
        d = rotear("quero outro tópico", estado_com_exercicio())
        self.assertEqual(d.intencao, "abandonar_exercicio")

    def test_negacao_nao_configura_invencao(self):
        d = rotear("não invente nada, explique o Strategy", self.e)
        self.assertNotEqual(d.motivo, "invencao")

    def test_saudacao_com_pontuacao(self):
        self.assertEqual(rotear("oi!", self.e).motivo, "saudacao")

    def test_llm_so_quando_ambiguo(self):
        chamadas = []
        e = EstadoAluno(padrao="Strategy")
        d = rotear("hmm interessante isso", e, lambda t, p: chamadas.append(t) or "custos")
        self.assertEqual((d.intencao, d.motivo), ("custos", "llm"))
        rotear("o que é strategy", e, lambda t, p: chamadas.append(t) or "custos")
        self.assertEqual(len(chamadas), 1)


class ValidadoresTest(unittest.TestCase):
    def test_exercicio_revela_termo(self):
        txt = "**Cenário:** use Strategy\n**Sua tarefa:** x\nMinha resposta"
        self.assertTrue(any("Strategy" in p for p in validar_exercicio(txt, STRATEGY)))

    def test_exercicio_fixo_e_valido(self):
        for p in PADROES.values():
            self.assertEqual(validar_exercicio(p.exercicio_fixo, p), [], p.nome)

    def test_exercicio_que_responde_a_si_mesmo_e_invalido(self):
        txt = ("**Cenário:** use o padrão\n**Sua tarefa:** x\n"
               "Minha resposta: eu criaria uma interface comum")
        self.assertTrue(any("resposta" in p for p in validar_exercicio(txt, STRATEGY)))

    def test_regras_do_exercicio_nao_nomeiam_padroes(self):
        from agente.prompts import PROMPT_EXERCICIO, REGRAS_EXERCICIO
        for texto in (REGRAS_EXERCICIO, PROMPT_EXERCICIO):
            for termo in ("Strategy", "Adapter", "Context", "Target", "Adaptee"):
                self.assertNotIn(termo, texto)

    def test_context_em_adapter_e_invalido(self):
        self.assertTrue(validar_texto("O Context chama o adaptador.", ADAPTER, "mecanismo", 100))
        self.assertFalse(validar_texto("O Context chama o adaptador.", ADAPTER, "comparar", 100))

    def test_codigo_bloqueado_em_explicacao(self):
        self.assertTrue(validar_texto("```java\nx\n```", STRATEGY, "conceito", 100))

    def test_veredito(self):
        self.assertEqual(extrair_veredito("ok. VEREDITO: OK")[0], "OK")
        self.assertEqual(extrair_veredito("erro X. VEREDITO: CORRIGIR"), ("CORRIGIR", "erro X."))
        self.assertEqual(extrair_veredito("sem marca")[0], "INDEFINIDO")

    def test_feedback_exige_resultado_e_conceito(self):
        sem_marcas = "**Pergunta para avançar:** e agora?"
        self.assertTrue(validar_feedback(sem_marcas, exigir_resultado=True))
        completo = sem_marcas + "\nRESULTADO: PARCIAL\nCONCEITO: injeção"
        self.assertEqual(validar_feedback(completo, exigir_resultado=True), [])

    def test_feedback_que_copia_template_e_rejeitado(self):
        copia = ('**O que você escreveu:** "trecho literal da resposta, até 30 palavras"\n'
                 "**Pergunta para avançar:** e agora?\nRESULTADO: PARCIAL\nCONCEITO: x")
        self.assertTrue(validar_feedback(copia, exigir_resultado=True))

    def test_lacuna_nao_e_erro(self):
        from agente.validadores import veredito_efetivo
        self.assertEqual(veredito_efetivo("CORRIGIR", "faltou mencionar a interface comum"), "OK")
        self.assertEqual(veredito_efetivo("CORRIGIR", "inventa um participante"), "CORRIGIR")
        real = ("Motivo: O texto trata corretamente do padrão Strategy, usa uma analogia apropriada e "
                "não contradiz os fatos verificados. No entanto, faltou mencionar a interface comum "
                "(Strategy) e a delegação do Context.")
        self.assertEqual(veredito_efetivo("CORRIGIR", real), "OK")  # caso real do log

    def test_resultado(self):
        limpo, r, c = extrair_resultado("Bom.\nRESULTADO: CORRETO\nCONCEITO: injeção")
        self.assertEqual((limpo, r, c), ("Bom.", "CORRETO", "injeção"))


class ConhecimentoTest(unittest.TestCase):
    def test_strategy_context_sem_condicional(self):
        codigo = STRATEGY.exemplo_java
        navegador = codigo.split("class Navegador")[1].split("public class Main")[0]
        self.assertNotIn("if (", navegador)
        self.assertNotIn("switch", navegador)

    def test_fatos_por_topico(self):
        f = ADAPTER.fatos(("custos",))
        self.assertIn("CONSEQUÊNCIAS", f); self.assertNotIn("PARTICIPANTES", f)

    @unittest.skipUnless(shutil.which("javac"), "JDK não instalado")
    def test_java_compila(self):
        for p in PADROES.values():
            with tempfile.TemporaryDirectory() as d:
                (Path(d) / "Main.java").write_text(p.exemplo_java, encoding="utf-8")
                r = subprocess.run(["javac", "Main.java"], cwd=d, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)


class FluxoTest(unittest.TestCase):
    def test_entrada_vazia(self):
        self.assertIn("Não recebi", Tutor(MotorFalso(), registrar=False).responder(""))

    def test_recusas_nao_chamam_modelo(self):
        m = MotorFalso(); t = Tutor(m, registrar=False)
        t.responder("Invente um padrão chamado Z"); t.responder("Me entregue a solução completa")
        self.assertEqual(m.recebidos, [])

    def test_aula_curta_com_pergunta_e_estado(self):
        m = MotorFalso(["Strategy troca algoritmos. Qual varia no seu if/else?", "ok VEREDITO: OK"])
        t = Tutor(m, registrar=False)
        r = t.responder("O que é o Strategy?")
        self.assertIn("?", r)
        self.assertEqual(t.estado.ja_viu("Strategy"), ["contexto"])
        self.assertEqual(t.estado.padrao, "Strategy")

    def test_guardiao_corrigir_regenera_uma_vez(self):
        m = MotorFalso(["Texto errado?", "erro. VEREDITO: CORRIGIR"],
                       ["Texto bom. E agora?", "VEREDITO: OK"])
        t = Tutor(m, registrar=False)
        r = t.responder("O que é o Strategy?")
        self.assertIn("Texto bom", r)
        self.assertIn("CORREÇÃO OBRIGATÓRIA", m.recebidos[1][1]["correcao"])

    def test_dois_corrigir_usa_fallback_verificado(self):
        ruim = ["Texto ruim?", "x. VEREDITO: CORRIGIR"]
        t = Tutor(MotorFalso(ruim, ruim), registrar=False)
        self.assertIn(STRATEGY.definicao, t.responder("O que é o Strategy?"))

    def test_exemplo_usa_codigo_verificado(self):
        m = MotorFalso(["**O que observar:** ok. **Se amanhã...:** ok.", "VEREDITO: OK"])
        r = Tutor(m, registrar=False).responder("Dê um exemplo de Adapter em Java")
        self.assertIn("class PixAdapter", r)

    def test_exercicio_com_vazamento_cai_no_fixo_e_fica_pendente(self):
        vaza = ["**Cenário:** use Strategy\n**Sua tarefa:** x\nMinha resposta", "VEREDITO: OK"]
        t = Tutor(MotorFalso(vaza, vaza), registrar=False)
        r = t.responder("Me dê um exercício sobre Strategy")
        self.assertNotIn("Strategy", r)
        self.assertIsNotNone(t.estado.exercicio)

    def test_exercicio_nao_recebe_nome_do_padrao_no_estado(self):
        valido = ["**Cenário:** uma loja precisa variar o cálculo.\n"
                  "**Sua tarefa:** identifique o que varia.\nMinha resposta", "VEREDITO: OK"]
        m = MotorFalso(valido)
        Tutor(m, registrar=False).responder("Me dê um exercício sobre Strategy")
        enviado = m.recebidos[0][1]
        for termo in ("Strategy", "Context", "Adapter", "Target", "Adaptee"):
            self.assertNotIn(termo, enviado["estado"])
            self.assertNotIn(termo, enviado["fatos"])

    def test_avaliacao_com_template_cai_no_fixo(self):
        copia = ['**O que você escreveu:** "trecho literal da resposta, até 30 palavras"\n'
                 "**Pergunta para avançar:** e agora?\nRESULTADO: PARCIAL\nCONCEITO: x",
                 "VEREDITO: OK"]
        t = Tutor(MotorFalso(copia, copia), registrar=False)
        t.estado = estado_com_exercicio()
        r = t.responder("Minha resposta: criaria uma interface e injetaria a regra")
        self.assertIn("Não consegui avaliar", r)

    def test_avaliacao_registra_dificuldade(self):
        fb = ("**O que você escreveu:** \"x\"\n**Pergunta para avançar:** e agora?\n"
              "RESULTADO: PARCIAL\nCONCEITO: quem escolhe a regra")
        t = Tutor(MotorFalso([fb, "VEREDITO: OK"]), registrar=False)
        t.estado = estado_com_exercicio()
        r = t.responder("Minha resposta: criaria uma interface e injetaria a regra")
        self.assertNotIn("RESULTADO", r)
        self.assertIn("quem escolhe a regra", t.estado.dificuldades)
        self.assertIsNotNone(t.estado.exercicio)  # continua pendente

    def test_abandonar_exercicio_limpa_estado(self):
        t = Tutor(MotorFalso(), registrar=False)
        t.estado = estado_com_exercicio()
        r = t.responder("quero outro tópico")
        self.assertIn("deixei o exercício", r)
        self.assertIsNone(t.estado.exercicio)
        self.assertIsNone(t.estado.exercicio_padrao)

    def test_feedback_sem_resultado_cai_no_fixo(self):
        incompleto = (["**O que você escreveu:** \"x\"\n**Pergunta para avançar:** e agora?",
                       "VEREDITO: OK"],
                      ["**O que você escreveu:** \"x\"\n**Pergunta para avançar:** e agora?",
                       "VEREDITO: OK"])
        t = Tutor(MotorFalso(*incompleto), registrar=False)
        t.estado = estado_com_exercicio()
        r = t.responder("Minha resposta: criaria uma interface e injetaria a regra")
        self.assertIn("Não consegui avaliar", r)
        self.assertIsNotNone(t.estado.exercicio)

    def test_bloco_de_codigo_e_removido_sem_rejeitar(self):
        m = MotorFalso(["Strategy troca algoritmos.\n```java\nx\n```\nFaz sentido?", "VEREDITO: OK"])
        t = Tutor(m, registrar=False)
        r = t.responder("O que é o Strategy?")
        self.assertNotIn("```", r); self.assertEqual(len(m.recebidos), 1)

    def test_chamada_orfa_de_pseudocodigo_e_removida(self):
        m = MotorFalso(["Vamos ao exemplo.\n\nAqui está um exemplo de pseudocódigo:\n\n"
                        "```\nx\n```\n\nAgora, quando evitar.", "VEREDITO: OK"])
        t = Tutor(m, registrar=False)
        r = t.responder("Quando devo evitar o Strategy?")
        self.assertNotIn("pseudocódigo", r)
        self.assertIn("Agora, quando evitar", r)

    def test_linha_que_anuncia_codigo_e_removida(self):
        m = MotorFalso(["Vamos ver como isso fica:\n\n```java\nx\n```\n\nFaz sentido?",
                        "VEREDITO: OK"])
        r = Tutor(m, registrar=False).responder("O que é o Strategy?")
        self.assertNotIn("Vamos ver", r)
        self.assertIn("Faz sentido", r)

    def test_conversa_passa_pelo_modelo(self):
        m = MotorFalso(["Oi! Sou tutor de Strategy e Adapter. Por onde quer começar?"])
        r = Tutor(m, registrar=False).responder("Continue a explicacao")
        self.assertIn("Por onde", r); self.assertEqual(m.recebidos[0][0], ["tutor"])

    def test_conversa_com_falha_usa_mensagem_fixa(self):
        r = Tutor(MotorFalso(erro=ConnectionError()), registrar=False).responder("oi")
        self.assertIn("Strategy e Adapter", r)

    def test_fora_de_escopo_longo_demais_usa_fixa(self):
        m = MotorFalso(["palavra " * 200])
        r = Tutor(m, registrar=False).responder("Explique o Observer")
        self.assertIn("Observer", r); self.assertLess(len(r.split()), 80)

    def test_falha_do_modelo(self):
        r = Tutor(MotorFalso(erro=ConnectionError()), registrar=False).responder("O que é o Strategy?")
        self.assertIn("Ollama", r)

    def test_historico_resume_falas_longas(self):
        e = EstadoAluno(); e.registrar("sistema", "palavra " * 500)
        self.assertLess(len(e.historico_curto()), 400)


if __name__ == "__main__":
    unittest.main()
