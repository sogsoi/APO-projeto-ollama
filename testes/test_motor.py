"""Testes da detecção de modelo e da URL do Ollama (sem rede)."""

import os
import unittest
from unittest.mock import patch

from agente import motor


class BaseUrlTest(unittest.TestCase):
    def test_padrao(self):
        with patch.dict(os.environ, {"OLLAMA_HOST": ""}):
            self.assertEqual(motor._base_url(), "http://127.0.0.1:11434")

    def test_host_sem_esquema(self):
        with patch.dict(os.environ, {"OLLAMA_HOST": "localhost:11500"}):
            self.assertEqual(motor._base_url(), "http://localhost:11500")

    def test_bind_all_vira_localhost(self):
        with patch.dict(os.environ, {"OLLAMA_HOST": "0.0.0.0:11434"}):
            self.assertEqual(motor._base_url(), "http://127.0.0.1:11434")

    def test_sem_porta_usa_11434(self):
        with patch.dict(os.environ, {"OLLAMA_HOST": "localhost"}):
            self.assertEqual(motor._base_url(), "http://localhost:11434")

    def test_so_porta(self):
        with patch.dict(os.environ, {"OLLAMA_HOST": ":11434"}):
            self.assertEqual(motor._base_url(), "http://127.0.0.1:11434")

    def test_https_sem_porta_nao_inventa_11434(self):
        with patch.dict(os.environ, {"OLLAMA_HOST": "https://ollama.example.com"}):
            self.assertEqual(motor._base_url(), "https://ollama.example.com")


class EscolherModeloTest(unittest.TestCase):
    def test_prefere_7b(self):
        self.assertEqual(
            motor.escolher_modelo(["qwen2.5:3b", "qwen2.5:7b"]), "qwen2.5:7b"
        )

    def test_cai_para_3b(self):
        self.assertEqual(motor.escolher_modelo(["qwen2.5:3b"]), "qwen2.5:3b")

    def test_aceita_variante(self):
        self.assertEqual(
            motor.escolher_modelo(["qwen2.5:7b-instruct-q4_K_M"]),
            "qwen2.5:7b-instruct-q4_K_M",
        )

    def test_aceita_outro_modelo_instalado(self):
        self.assertEqual(motor.escolher_modelo(["llama3.2:3b"]), "llama3.2:3b")

    def test_ignora_embedding(self):
        self.assertEqual(
            motor.escolher_modelo(["nomic-embed-text:latest", "llama3.2:3b"]),
            "llama3.2:3b",
        )

    def test_prefere_qwen_menor_a_modelo_aleatorio(self):
        self.assertEqual(
            motor.escolher_modelo(["llama3.2:3b", "qwen2.5:1.5b"]), "qwen2.5:1.5b"
        )

    def test_entre_desconhecidos_prefere_o_maior(self):
        self.assertEqual(
            motor.escolher_modelo(["llama3.2:1b", "llama3.2:3b"]), "llama3.2:3b"
        )

    def test_sem_modelo_de_conversa(self):
        self.assertIsNone(motor.escolher_modelo(["nomic-embed-text:latest"]))


class DetectarModeloTest(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"MODELO_LLM": ""})
        self.env.start()
        self.addCleanup(self.env.stop)

    @patch("agente.motor._listar_instalados", return_value=["qwen2.5:3b"])
    def test_detecta_3b(self, _):
        self.assertEqual(motor.detectar_modelo("http://127.0.0.1:11434"),
                         "ollama/qwen2.5:3b")

    @patch("agente.motor._listar_instalados", side_effect=OSError("offline"))
    def test_ollama_fora_do_ar(self, _):
        with self.assertRaises(motor.ModeloIndisponivel) as ctx:
            motor.detectar_modelo("http://127.0.0.1:11434")
        self.assertIn("ollama ps", str(ctx.exception))

    @patch("agente.motor._listar_instalados", return_value=["nomic-embed-text:latest"])
    def test_nenhum_modelo_de_conversa(self, _):
        with self.assertRaises(motor.ModeloIndisponivel) as ctx:
            motor.detectar_modelo("http://127.0.0.1:11434")
        self.assertIn("ollama pull", str(ctx.exception))

    @patch("agente.motor._listar_instalados", return_value=["llama3.2:3b"])
    def test_modelo_fora_da_lista_avisa_mas_usa(self, _):
        with self.assertLogs("agente.motor", level="WARNING") as logs:
            self.assertEqual(motor.detectar_modelo("http://127.0.0.1:11434"),
                             "ollama/llama3.2:3b")
        self.assertIn("não está na lista recomendada", "\n".join(logs.output))

    @patch("agente.motor._listar_instalados", return_value=["qwen2.5:3b", "qwen2.5:7b"])
    def test_modelo_llm_forcado(self, _):
        with patch.dict(os.environ, {"MODELO_LLM": "qwen2.5:3b"}):
            self.assertEqual(motor.detectar_modelo("http://127.0.0.1:11434"),
                             "ollama/qwen2.5:3b")

    @patch("agente.motor._listar_instalados", return_value=["qwen2.5:3b"])
    def test_modelo_llm_ausente(self, _):
        with patch.dict(os.environ, {"MODELO_LLM": "qwen2.5:7b"}):
            with self.assertRaises(motor.ModeloIndisponivel) as ctx:
                motor.detectar_modelo("http://127.0.0.1:11434")
        self.assertIn("ollama pull qwen2.5:7b", str(ctx.exception))


class MotorCrewAITest(unittest.TestCase):
    def test_construtor_nao_detecta(self):
        with patch("agente.motor.detectar_modelo",
                   side_effect=AssertionError("detectou cedo demais")):
            m = motor.MotorCrewAI()
        self.assertIsNone(m.modelo)
        self.assertIsNone(m._llm)

    def test_normaliza_prefixo(self):
        self.assertEqual(motor.MotorCrewAI("qwen2.5:3b").modelo, "ollama/qwen2.5:3b")
        self.assertEqual(motor.MotorCrewAI("ollama/qwen2.5:3b").modelo,
                         "ollama/qwen2.5:3b")
