"""CrewAI v1.x-compatible bootstrap example.

This script demonstrates the v1.x constructor shape where the LLM is passed as
an object and Agent/Task use typed models. Run this in a separate venv that
has `crewai` and `python-dotenv` installed.

Usage:
  python agents/crew/bootstrap.py
"""

import os
from dotenv import load_dotenv

# Attempt to import CrewAI v1.x API; if missing, show an actionable message.
try:
    from crewai import Agent, Task, Crew, LLM
except Exception:
    print("crewai v1.x is not installed in this environment.\nRun: pip install crewai")
    Agent = Task = Crew = LLM = None


def main():
    load_dotenv()

    if not (Agent and Task and Crew and LLM):
        print("Missing crewai package; please install in a separate agents venv.")
        return

    # Initialize the LLM object (v1.x expects an object, not a string)
    llm = LLM(model=os.getenv("AGENT_MODEL", "gpt-4o-mini"))

    # Define agents using typed constructors
    planner = Agent(
        role="Planner",
        goal="Define FitTwin build tasks clearly and concisely",
        backstory="You are a methodical planner for a fast-moving AI startup.",
        llm=llm,
        verbose=True,
    )

    executor = Agent(
        role="Executor",
        goal="Turn the Planner's goals into actionable steps",
        backstory="You write precise, step-by-step checklists for developers.",
        llm=llm,
        verbose=True,
    )

    # Define tasks bound to agents
    plan_task = Task(
        description="List three next steps for FitTwin's iPhone upload feature.",
        agent=planner,
        expected_output="Three clearly phrased next steps.",
    )

    execute_task = Task(
        description="Turn the Planner's output into a numbered checklist developers can follow.",
        agent=executor,
        expected_output="A numbered checklist with 3-5 clear steps.",
    )

    # Assemble the crew and run
    crew = Crew(agents=[planner, executor], tasks=[plan_task, execute_task])

    result = crew.kickoff()
    print("\n=== Crew Output ===\n")
    print(result)


if __name__ == "__main__":
    main()
