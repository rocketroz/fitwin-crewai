"""Bootstrap example to run a tiny CrewAI crew locally.

Usage (recommended to run in a separate venv):

python agents/crew/bootstrap.py

Notes:
- Create and activate a separate venv for agent work (do not mix with backend venv)
  python3 -m venv .venv-agents
  source .venv-agents/bin/activate
  pip install crewai python-dotenv

This script is intentionally small and demonstrates two cooperating agents.
Replace model names, tokens, and tasks as appropriate for your environment.
"""

import os
from dotenv import load_dotenv

# Try to import crewai; if missing, print a helpful message
try:
    from crewai import Agent, Task, Crew
except Exception:
    print("crewai is not installed in the current environment.\nRun: pip install crewai")
    Agent = None
    Task = None
    Crew = None

load_dotenv()

# Minimal example: two agents collaborate — planner and executor
if Agent and Task and Crew:
    planner = Agent(role="Planner", goal="Define FitTwin build tasks", llm=os.getenv("AGENT_MODEL", "gpt-4o-mini"))
    executor = Agent(role="Executor", goal="Summarize Planner output into actions", llm=os.getenv("AGENT_MODEL", "gpt-4o-mini"))

    task1 = Task(description="List three next steps for FitTwin's iPhone upload feature", agent=planner)
    task2 = Task(description="Convert Planner output into a structured to-do list", agent=executor)

    crew = Crew(agents=[planner, executor], tasks=[task1, task2])

    if __name__ == "__main__":
        result = crew.kickoff()
        print(result)
else:
    if __name__ == "__main__":
        print("Install crewai in a separate venv, then re-run this script.")
