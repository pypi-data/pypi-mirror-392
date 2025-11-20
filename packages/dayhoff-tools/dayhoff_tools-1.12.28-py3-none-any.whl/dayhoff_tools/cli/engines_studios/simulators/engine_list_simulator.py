#!/usr/bin/env python3
"""Simulator for engine list output - iterate on design locally without AWS.

This lets you quickly see how the list command output looks with different
engine states and configurations.

Usage:
    python dayhoff_tools/cli/engines_studios/simulators/engine_list_simulator.py                # Show all scenarios
    python dayhoff_tools/cli/engines_studios/simulators/engine_list_simulator.py --scenario few # Show specific scenario
    python dayhoff_tools/cli/engines_studios/simulators/engine_list_simulator.py --env prod     # Simulate different environment
"""

import argparse
import sys
from typing import Any


def colorize(text: str, color_code: str) -> str:
    """Apply ANSI color code to text."""
    return f"\033[{color_code}m{text}\033[0m"


def format_list_output(engines: list[dict[str, Any]], env: str = "dev") -> None:
    """Format and print engine list output matching the actual CLI."""

    # Header with blue account name
    print(f"Engines for AWS Account {colorize(env, '34')}\n")

    if not engines:
        print("No engines found")
        return

    # Table header
    print(f"{'Name':<12} {'State':<12} {'User':<12} {'Type':<12} {'Instance ID':<20}")
    print("-" * 72)

    # Table rows
    for engine in engines:
        name = engine.get("name", "unknown")[:11]
        state = engine.get("state", "unknown")[:11]
        user = engine.get("user", "unknown")[:11]
        engine_type = engine.get("engine_type", "unknown")[:11]
        instance_id = engine.get("instance_id", "unknown")

        # Color the state
        if state == "running":
            state_display = colorize(f"{state:<12}", "32")  # Green
        elif state in ["starting", "stopping", "pending"]:
            state_display = colorize(f"{state:<12}", "33")  # Yellow
        elif state == "stopped":
            state_display = colorize(f"{state:<12}", "37")  # White
        else:
            state_display = f"{state:<12}"  # No color for other states

        print(
            f"{name:<12} {state_display} {user:<12} {engine_type:<12} {instance_id:<20}"
        )

    print(f"\nTotal: {len(engines)} engine(s)")


def generate_scenarios() -> dict[str, dict[str, Any]]:
    """Generate various test scenarios for list output."""

    scenarios = {}

    # Scenario 1: Single running engine
    scenarios["single"] = {
        "name": "Single Running Engine",
        "engines": [
            {
                "name": "alice-gpu",
                "state": "running",
                "user": "alice",
                "engine_type": "gpu",
                "instance_id": "i-0123456789abcdef0",
            }
        ],
        "env": "dev",
    }

    # Scenario 2: Few engines with various states
    scenarios["few"] = {
        "name": "Few Engines - Mixed States",
        "engines": [
            {
                "name": "alice-gpu",
                "state": "running",
                "user": "alice",
                "engine_type": "gpu",
                "instance_id": "i-0123456789abcdef0",
            },
            {
                "name": "bob-cpu",
                "state": "stopped",
                "user": "bob",
                "engine_type": "cpu",
                "instance_id": "i-1234567890abcdef1",
            },
            {
                "name": "charlie",
                "state": "starting",
                "user": "charlie",
                "engine_type": "cpu",
                "instance_id": "i-2345678901abcdef2",
            },
        ],
        "env": "sand",
    }

    # Scenario 3: Many engines (production-like)
    scenarios["many"] = {
        "name": "Many Engines - Production",
        "engines": [
            {
                "name": "alice-main",
                "state": "running",
                "user": "alice",
                "engine_type": "gpu",
                "instance_id": "i-0123456789abcdef0",
            },
            {
                "name": "bob-exp1",
                "state": "running",
                "user": "bob",
                "engine_type": "cpu",
                "instance_id": "i-1234567890abcdef1",
            },
            {
                "name": "bob-exp2",
                "state": "stopped",
                "user": "bob",
                "engine_type": "cpu",
                "instance_id": "i-2345678901abcdef2",
            },
            {
                "name": "charlie-gpu",
                "state": "running",
                "user": "charlie",
                "engine_type": "gpu",
                "instance_id": "i-3456789012abcdef3",
            },
            {
                "name": "diana-dev",
                "state": "running",
                "user": "diana",
                "engine_type": "cpu",
                "instance_id": "i-4567890123abcdef4",
            },
            {
                "name": "eve-test",
                "state": "stopping",
                "user": "eve",
                "engine_type": "cpu",
                "instance_id": "i-5678901234abcdef5",
            },
            {
                "name": "frank-prod",
                "state": "running",
                "user": "frank",
                "engine_type": "gpu",
                "instance_id": "i-6789012345abcdef6",
            },
        ],
        "env": "prod",
    }

    # Scenario 4: Empty list
    scenarios["empty"] = {
        "name": "No Engines",
        "engines": [],
        "env": "dev",
    }

    # Scenario 5: All transitional states
    scenarios["transitions"] = {
        "name": "Transitional States",
        "engines": [
            {
                "name": "engine1",
                "state": "starting",
                "user": "alice",
                "engine_type": "cpu",
                "instance_id": "i-0123456789abcdef0",
            },
            {
                "name": "engine2",
                "state": "stopping",
                "user": "bob",
                "engine_type": "cpu",
                "instance_id": "i-1234567890abcdef1",
            },
            {
                "name": "engine3",
                "state": "pending",
                "user": "charlie",
                "engine_type": "gpu",
                "instance_id": "i-2345678901abcdef2",
            },
        ],
        "env": "sand",
    }

    return scenarios


def main():
    parser = argparse.ArgumentParser(
        description="Simulate engine list output for design iteration"
    )
    parser.add_argument(
        "--scenario",
        choices=["single", "few", "many", "empty", "transitions", "all"],
        default="all",
        help="Which scenario to display (default: all)",
    )
    parser.add_argument(
        "--env",
        choices=["dev", "sand", "prod"],
        help="Override environment for display",
    )

    args = parser.parse_args()

    scenarios = generate_scenarios()

    if args.scenario == "all":
        # Show all scenarios
        for _, scenario_data in scenarios.items():
            print("\n" + "=" * 80)
            print(f"SCENARIO: {scenario_data['name']}")
            print("=" * 80 + "\n")

            env = args.env if args.env else scenario_data["env"]
            format_list_output(scenario_data["engines"], env)
            print()  # Extra newline between scenarios
    else:
        # Show specific scenario
        scenario_data = scenarios[args.scenario]
        print(f"\nSCENARIO: {scenario_data['name']}\n")

        env = args.env if args.env else scenario_data["env"]
        format_list_output(scenario_data["engines"], env)


if __name__ == "__main__":
    main()
