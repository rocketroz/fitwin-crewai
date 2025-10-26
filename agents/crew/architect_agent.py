from crewai import Agent, Task, Crew, LLM

llm = LLM(model="gpt-4o")

architect = Agent(
    role="Architect",
    goal="Produce a concise, actionable build plan for the next 48 hours of the FitTwin MVP.",
    backstory="Senior engineer who values clear APIs, privacy, and measurable success criteria.",
    allow_delegation=False,
    verbose=False,
    llm=llm,
)

plan_task = Task(
    description=(
        "Write a short 10-step plan to implement: "
        "1) two-photo capture client stub, "
        "2) FastAPI measurement-job facade with a stubbed response, "
        "3) Supabase schema migration and RLS check, "
        "4) a GET dmaas endpoint that returns the latest measurements and a one-line recommendation. "
        "Each step must include the exact file to edit or create, a one-line command to run, "
        "and the acceptance test that proves it works."
    ),
    expected_output="A numbered list of 10 steps with file paths, commands, and acceptance tests.",
    agent=architect,
)

crew = Crew(agents=[architect], tasks=[plan_task])
if __name__ == "__main__":
    print(crew.kickoff())
