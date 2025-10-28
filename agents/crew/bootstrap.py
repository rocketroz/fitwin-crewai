import os
from crewai import Agent, Task, Crew, LLM
from agents.client.api import dmaas_latest

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found in environment.")
    llm = LLM(model=os.getenv("AGENT_MODEL", "gpt-4o-mini"), api_key=api_key)

    planner = Agent(
        role="Planner",
        goal="Inspect FitTwin API data and propose next engineering steps",
        backstory="You think like a staff engineer who ships.",
        llm=llm,
        verbose=True,
    )

    executor = Agent(
        role="Executor",
        goal="Turn plans into a numbered, actionable checklist",
        backstory="You write precise steps that run today.",
        llm=llm,
        verbose=True,
    )

        # Pull live data from the backend
        data = {}
        try:
            data = dmaas_latest()
        except Exception as e:
            data = {"error": f"Could not reach /dmaas/latest: {e}"}
import os
from crewai import Agent, Task, Crew, LLM
from agents.client.api import dmaas_latest

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment.")
    llm = LLM(model=os.getenv("AGENT_MODEL", "gpt-4o-mini"), api_key=api_key)

    planner = Agent(
        role="Planner",
        goal="Inspect live FitTwin API data and describe implications for the iPhone upload feature.",
        backstory="You think like a staff engineer who ships pragmatic solutions.",
        llm=llm,
        verbose=True,
    )

    executor = Agent(
        role="Executor",
        goal="Turn the plan into a numbered checklist with concrete steps.",
        backstory="You write precise, do-this-now instructions for developers.",
        llm=llm,
        verbose=True,
    )

    # Pull live data from the backend
    data = {}
    try:
        data = dmaas_latest()
    except Exception as e:
        data = {"error": f"Could not reach /dmaas/latest: {e}"}

    t1 = Task(
        description=(
            "Given this /dmaas/latest JSON, briefly explain what it shows and list two implications "
            "for implementing the iPhone upload feature:\n\n"
            f"{data}"
        ),
        agent=planner,
        expected_output="One short paragraph and two bullet points on implications.",
    )

    t2 = Task(
        description="Convert the planner notes into a numbered checklist with 3 to 5 concrete steps.",
        agent=executor,
        expected_output="A numbered checklist with specific commands, files, or endpoints."
    )

    result = Crew(agents=[planner, executor], tasks=[t1, t2]).kickoff()
    print("\n=== Crew Output ===\n")
    print(result)

if __name__ == "__main__":
    main()
