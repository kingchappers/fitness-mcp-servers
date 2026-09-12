"""Integration tests — call the real Hevy API and check response sizes.

Run with:
    HEVY_INTEGRATION_TESTS=1 HEVY_API_KEY=<key> poetry run pytest tests/integration/ -v -s

Per CLAUDE.md's response size policy: < 20,000 chars is fine, 20,000-100,000
warrants review, > 100,000 must be reduced before the tool is usable.
"""

from __future__ import annotations

import json
import os

import pytest

import mcp_hevy.client as client_module
from mcp_hevy.client import get_client

if not os.getenv("HEVY_INTEGRATION_TESTS"):
    pytest.skip("Set HEVY_INTEGRATION_TESTS=1 to run", allow_module_level=True)


@pytest.fixture(autouse=True)
def reset_client() -> None:
    client_module._client = None


def _char_size(result_text: str) -> int:
    return len(result_text)


def test_get_workouts_response_size() -> None:
    from mcp_hevy.tools.workouts import DISPATCH

    client = get_client()
    result = DISPATCH["get_workouts"](client, {"page": 1, "page_size": 5})
    size = _char_size(result[0].text)
    print(f"\nget_workouts (pageSize=5) size: {size} chars")
    assert size < 100_000, f"get_workouts is {size} chars — must add _summarize_workouts"


def test_get_workout_response_size_for_single_detailed_workout() -> None:
    from mcp_hevy.tools.workouts import DISPATCH

    client = get_client()
    workouts_result = DISPATCH["get_workouts"](client, {"page": 1, "page_size": 1})
    workouts_data = json.loads(workouts_result[0].text)
    workout_list = workouts_data.get("workouts", [])
    if not workout_list:
        pytest.skip("No workouts logged on this account to fetch details for")
    workout_id = workout_list[0]["id"]

    result = DISPATCH["get_workout"](client, {"workout_id": workout_id})
    size = _char_size(result[0].text)
    print(f"\nget_workout (single, id={workout_id}) size: {size} chars")
    assert size < 100_000, f"get_workout is {size} chars — must add _summarize_workout"


def test_get_exercise_history_response_size() -> None:
    from mcp_hevy.tools.exercises import DISPATCH as EXERCISES_DISPATCH
    from mcp_hevy.tools.workouts import DISPATCH as WORKOUTS_DISPATCH

    client = get_client()
    workouts_result = WORKOUTS_DISPATCH["get_workouts"](client, {"page": 1, "page_size": 1})
    workouts_data = json.loads(workouts_result[0].text)
    workout_list = workouts_data.get("workouts", [])
    if not workout_list:
        pytest.skip("No workouts logged on this account")
    exercise_list = workout_list[0].get("exercises", [])
    if not exercise_list:
        pytest.skip("No exercises found on the account's most recent workout")
    template_id = exercise_list[0]["exercise_template_id"]

    result = EXERCISES_DISPATCH["get_exercise_history"](
        client, {"exercise_template_id": template_id}
    )
    size = _char_size(result[0].text)
    print(f"\nget_exercise_history (id={template_id}) size: {size} chars")
    assert size < 100_000, f"get_exercise_history is {size} chars — must add _summarize_history"


def test_get_body_measurements_response_size() -> None:
    from mcp_hevy.tools.body import DISPATCH

    client = get_client()
    result = DISPATCH["get_body_measurements"](client, {"page": 1, "page_size": 5})
    size = _char_size(result[0].text)
    print(f"\nget_body_measurements size: {size} chars")
    assert size < 100_000
