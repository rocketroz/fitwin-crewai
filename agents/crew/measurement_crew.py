"""
CrewAI measurement crew aligned with the Manus implementation package.
"""

from __future__ import annotations

import os

from crewai import Agent, Crew, LLM, Task

from agents.tools.measurement_tools import recommend_sizes, validate_measurements


def create_measurement_crew() -> Crew:
    """Instantiate the measurement processing crew with strategic directives."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment.")

    llm = LLM(model=os.getenv("AGENT_MODEL", "gpt-4o-mini"), api_key=api_key)

    ceo = Agent(
        role="CEO",
        goal="Maintain <3% measurement error and ensure Supabase integration within 5 days and <$500 budget.",
        backstory=(
            "Lead the FitTwin DMaaS MVP delivery. Coordinate the Architect, ML Engineer, "
            "and DevOps agents, escalate calibration needs below the 97% accuracy threshold, "
            "and ensure data provenance policies are in place."
        ),
        llm=llm,
        verbose=True,
    )

    architect = Agent(
        role="Architect",
        goal="Implement Supabase schema and geometric equations for MediaPipe-based measurement calculation.",
        backstory=(
            "Design the data flow and schema for storing MediaPipe landmarks, photos, and normalized measurements. "
            "Call validate_measurements first, attempt one repair on obvious 422 errors, then escalate if needed."
        ),
        tools=[validate_measurements],
        llm=llm,
        verbose=True,
    )

    ml_engineer = Agent(
        role="ML Engineer",
        goal="Produce measurement accuracy estimates and sizing recommendations.",
        backstory=(
            "Build IP around MediaPipe-derived measurements, estimate accuracy, and surface flags for low confidence "
            "results. Use recommend_sizes on normalized data and return concise JSON outputs."
        ),
        tools=[recommend_sizes],
        llm=llm,
        verbose=True,
    )

    devops = Agent(
        role="DevOps",
        goal="Manage CI/CD, deployment, and infra under <$500 budget.",
        backstory=(
            "Handle GitHub Actions, Supabase provisioning, and TestFlight distribution while maintaining security "
            "and keeping costs down."
        ),
        llm=llm,
        verbose=True,
    )

    reviewer = Agent(
        role="Reviewer",
        goal="Validate compliance, cost, and security posture.",
        backstory=(
            "Act as an autonomous reviewer ensuring RLS policies, API key handling, and budget targets are satisfied "
            "before approving deployment."
        ),
        llm=llm,
        verbose=True,
    )

    validate_task = Task(
        description=(
            "Validate user-provided measurements or MediaPipe landmarks. Use validate_measurements, "
            "attempt one repair on clear 422 hints, and escalate to the CEO for unresolved issues or "
            "accuracy below 97%."
        ),
        agent=architect,
        expected_output="Normalized measurement data with confidence scores or an escalation note.",
    )

    recommend_task = Task(
        description=(
            "Use the Architect's normalized output to call recommend_sizes. Deliver JSON recommendations with "
            "confidence and model version metadata."
        ),
        agent=ml_engineer,
        expected_output="JSON recommendations including processed measurements and model version.",
    )

    review_task = Task(
        description=(
            "Review the validation and recommendation workflow for security, cost, and quality. "
            "Confirm RLS, API key hygiene, and <$500 budget adherence."
        ),
        agent=reviewer,
        expected_output="Review report noting outstanding issues or deployment approval.",
    )

    return Crew(
        agents=[ceo, architect, ml_engineer, devops, reviewer],
        tasks=[validate_task, recommend_task, review_task],
        verbose=True,
    )


def main() -> None:
    """Kick off the measurement crew with placeholder MediaPipe data."""
    crew = create_measurement_crew()
    sample_input = {
        "front_landmarks": {
            "landmarks": [],  # TODO: insert actual landmark data during calibration.
            "timestamp": "2025-10-26T15:00:00Z",
            "image_width": 1920,
            "image_height": 1080,
        },
        "side_landmarks": {
            "landmarks": [],
            "timestamp": "2025-10-26T15:00:05Z",
            "image_width": 1920,
            "image_height": 1080,
        },
        "front_photo_url": "https://storage.fittwin.com/photos/session123/front.jpg",
        "side_photo_url": "https://storage.fittwin.com/photos/session123/side.jpg",
        "session_id": "session123",
    }

    print("\n=== Starting Measurement Crew ===\n")
    print(f"Input: {sample_input}\n")
    result = crew.kickoff()
    print("\n=== Crew Output ===\n")
    print(result)


if __name__ == "__main__":
    main()
