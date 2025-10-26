"""agents/crew/bootstrap.py
CrewAI v1.x-compatible example using typed LLM objects.

"""

import os
from crewai import Agent, Task, Crew, LLM

def main():
    # Ensure API key is provided via environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment.")

    # Create the LLM object CrewAI expects
    llm = LLM(model=os.getenv("AGENT_MODEL", "gpt-4o-mini"), api_key=api_key)

    # Define the two cooperating agents
    planner = Agent(
        role="Planner",
        goal="Define FitTwin build tasks clearly and concisely",
        backstory="You are a technical planner who designs next steps for FitTwin's product roadmap.",
        llm=llm,
        verbose=True,
    )

    executor = Agent(
        role="Executor",
        goal="Turn plans into a numbered, actionable checklist",
        backstory="You translate abstract ideas into concise development steps.",
        llm=llm,
        verbose=True,
    )

    # Define tasks for each agent
    plan_task = Task(
        description="List three next steps for FitTwin's iPhone upload feature.",
        agent=planner,
        expected_output="Three short, clear next steps.",
    )

    execute_task = Task(
        description="Convert the Planner's output into a numbered checklist that developers can follow today.",
        agent=executor,
        expected_output="A numbered checklist with 3–5 steps.",
    )

    # Assemble and run the crew
    crew = Crew(agents=[planner, executor], tasks=[plan_task, execute_task])
    result = crew.kickoff()

    print("\n=== Crew Output ===\n")
    print(result)

if __name__ == "__main__":
    main()
