from crewai import LLM

llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434",
)

resposta = llm.call("Diga oi em uma frase")
print(resposta)
