from crewai import Agent, Task, Crew, LLM

llm = LLM(model="gpt-4o")

tester = Agent(
    role="Tester",
    goal="Reply with exactly OK",
    backstory="Sanity check for local setup",
    allow_delegation=False,
    verbose=False,
    llm=llm,
)

task = Task(
    description="Reply with exactly: OK",
    expected_output="OK",
    agent=tester,
)

crew = Crew(agents=[tester], tasks=[task])
print(crew.kickoff())
