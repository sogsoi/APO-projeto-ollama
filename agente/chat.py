"""Interface web opcional (Gradio). O comando padrão `python -m agente "..."` continua valendo."""

from .tutor import Tutor


def abrir() -> None:
    import gradio as gr

    tutor = Tutor()  # demonstração de um usuário por vez

    def conversar(mensagem, historico):
        if not historico:          # conversa nova na interface => memória nova
            tutor.reiniciar()
        return tutor.responder(mensagem)

    gr.ChatInterface(
        fn=conversar,
        title="Tutor de padrões de projeto",
        description="Strategy e Adapter. Cada resposta leva de 20 a 60 segundos no modelo local.",
        examples=["O que é o padrão Strategy?", "Me mostre um exemplo de Adapter em Java",
                  "Qual a diferença entre Strategy e Adapter?", "Me dê um exercício sobre Adapter"],
    ).launch()
