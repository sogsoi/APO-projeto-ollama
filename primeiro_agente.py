import sys
from crewai import Agent, Task, Crew, Process, LLM

llm = LLM(
    model="ollama/qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.5,
    timeout=300,
    context_window_size=8192,
)

tutor = Agent(
    role="Tutor de Princípios SOLID",
    goal="Ensinar os 5 princípios SOLID: o que cada um significa, "
         "o problema que resolve e como reconhecê-lo no código",
    backstory=(
        "Você é um professor de programação orientada a objetos, "
        "paciente e didático, especialista em princípios de design."
    ),
    llm=llm,
)

tarefa = Task(
    description="Responda à pergunta do estudante sobre os princípios SOLID: {pergunta}",
    expected_output="Explicação em português, com exemplo em Java, em até 200 palavras.",
    agent=tutor,
)

crew = Crew(
    agents=[tutor],
    tasks=[tarefa],
    process=Process.sequential,
)

pergunta = " ".join(sys.argv[1:]).strip()
if not pergunta:
    pergunta = "O que é o princípio da Responsabilidade Única?"

resultado = crew.kickoff(inputs={"pergunta": pergunta})
print(resultado.raw)
