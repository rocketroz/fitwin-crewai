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
Measurement crew for CrewAI multi-agent system.

This module defines the five agents (CEO, Architect, ML Engineer, DevOps, Reviewer)
with specific directives aligned to the DMaaS MVP strategy.
"""

import os
from crewai import Agent, Task, Crew, LLM
from agents.tools.measurement_tools import validate_measurements, recommend_sizes


def create_measurement_crew():
    """Create and configure the measurement processing crew with strategic directives."""
    
    # Ensure API key is provided
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment.")
    
    # Create LLM
    llm = LLM(model=os.getenv("AGENT_MODEL", "gpt-4o-mini"), api_key=api_key)
    
    # Define agents with strategic directives
    ceo = Agent(
        role="CEO",
        goal="Oversee MVP accuracy (<3% error) and Supabase integration within 5-day timeline and <$500 budget",
        backstory=(
            "You are the CEO of FitTwin, building a DMaaS platform for AI systems and retailers. "
            "Your directive: Achieve a deployable Supabase-backed API with MediaPipe-only measurement "
            "extraction within 5 days, with a budget constraint of <$500. "
            "You delegate tasks to the Architect, ML Engineer, and DevOps agents. "
            "You communicate with the user when input is needed or when errors cannot be resolved automatically. "
            "If MediaPipe accuracy falls below 97%, you trigger optional vendor API calibration."
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
    
    architect = Agent(
        role="Architect",
        goal="Implement Supabase schema and geometric equations for MediaPipe measurement calculation",
        backstory=(
            "You are a meticulous architect who plans the data flow and system design. "
            "Your directive: Prioritize Supabase and data security (RLS). Design schema for measurement "
            "provenance (storing raw photos, MediaPipe landmarks, calculated measurements). "
            "Implement geometric equations to calculate anthropometric measurements from MediaPipe landmarks. "
            "You call validate_measurements first, then pass the normalized result to recommend_sizes. "
            "If validation returns a 422 error with an obvious fix (like unit conversion or name typo), "
            "you attempt ONE repair and retry. If the fix fails or the error is complex, you escalate to the CEO."
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
    
    ml_engineer = Agent(
        role="ML Engineer",
        goal="Build internal model for measurement prediction and accuracy estimation",
        backstory=(
            "You are an ML engineer who builds the core IP: the proprietary measurement model. "
            "Your directive: Implement the data pipeline to ingest and normalize MediaPipe landmarks and "
            "vendor measurements (if used for calibration). Design the initial proprietary sizing model. "
            "You receive normalized measurements from the Architect and call recommend_sizes. "
            "You return the JSON result with no extra storytelling. "
            "You also estimate measurement accuracy and flag low-confidence results for CEO review."
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
    
    devops = Agent(
        role="DevOps",
        goal="Manage CI/CD, TestFlight deployment, and infrastructure (<$500 budget)",
        backstory=(
            "You are a DevOps engineer who handles infrastructure, CI/CD, and deployment. "
            "Your directive: Scaffold the Flutter/SwiftUI repo. Implement GitHub Actions for linting, "
            "testing, and automated deployment. Deploy to TestFlight for user testing. "
            "Provide final Supabase connection strings and DMaaS API keys. "
            "You work within a <$500 budget constraint, prioritizing free tiers (Supabase, GitHub Actions, TestFlight)."
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
    
    reviewer = Agent(
        role="Reviewer",
        goal="Validate cost and data security compliance before deployment",
        backstory=(
            "You are a code reviewer who critiques all code and infrastructure changes before the DevOps Agent commits them. "
            "Your directive: Check for security vulnerabilities, code quality issues, and alignment with the DMaaS strategy. "
            "Validate that cost constraints are met (<$500 for MVP). "
            "Ensure data security (RLS policies, API key authentication, secure photo storage). "
            "Provide feedback to the Architect and ML Engineer for improvements. "
            "This acts as an autonomous peer review to enhance security and code quality."
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
    
    # Define tasks
    validate_task = Task(
        description=(
            "Validate the user-provided measurement data or MediaPipe landmarks using the validate_measurements tool. "
            "If you receive a 422 error with a clear repair hint (e.g., wrong unit or typo in field name), "
            "attempt to fix it ONCE and retry. If the error persists or is unclear, escalate to the CEO. "
            "If accuracy estimate is >3%, flag for potential vendor calibration."
        ),
        agent=architect,
        expected_output="Normalized measurement data in centimeters with confidence scores, or an error report for the CEO.",
    )
    
    recommend_task = Task(
        description=(
            "Use the normalized measurements from the Architect to generate size recommendations. "
            "Call the recommend_sizes tool and return the result as JSON. "
            "Include confidence scores and model version for API consumers."
        ),
        agent=ml_engineer,
        expected_output="A JSON object with size recommendations, processed measurements, and model version.",
    )
    
    review_task = Task(
        description=(
            "Review the complete workflow (validation + recommendation) for security, cost, and quality. "
            "Check that RLS policies are in place, API keys are secure, and budget is <$500. "
            "Provide feedback if any issues are found."
        ),
        agent=reviewer,
        expected_output="A review report with any issues found, or confirmation that the system is ready for deployment.",
    )
    
    # Assemble crew
    crew = Crew(
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
    
    return crew


def main():
    """Run the measurement crew with sample input."""
    crew = create_measurement_crew()
    
    # Example input with MediaPipe landmarks (placeholder)
    sample_input = {
        "front_landmarks": {
            "landmarks": [],  # TODO: Add actual landmark data
            "timestamp": "2025-10-26T15:00:00Z",
            "image_width": 1920,
            "image_height": 1080
        },
        "side_landmarks": {
            "landmarks": [],  # TODO: Add actual landmark data
            "timestamp": "2025-10-26T15:00:05Z",
            "image_width": 1920,
            "image_height": 1080
        },
        "front_photo_url": "https://storage.fittwin.com/photos/session123/front.jpg",
        "side_photo_url": "https://storage.fittwin.com/photos/session123/side.jpg",
        "session_id": "session123"
    }
    
    print("\n=== Starting Measurement Crew ===\n")
    print(f"Input: {sample_input}\n")
    
    result = crew.kickoff()
    
    print("\n=== Crew Output ===\n")
    print(result)


if __name__ == "__main__":
    main()

