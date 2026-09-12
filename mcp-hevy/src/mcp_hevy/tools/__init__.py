from collections.abc import Callable
from typing import Any

import httpx
from mcp.types import TextContent, Tool

from mcp_hevy.tools.body import DISPATCH as _BODY_DISPATCH
from mcp_hevy.tools.body import TOOLS as _BODY_TOOLS
from mcp_hevy.tools.exercises import DISPATCH as _EXERCISE_DISPATCH
from mcp_hevy.tools.exercises import TOOLS as _EXERCISE_TOOLS
from mcp_hevy.tools.routines import DISPATCH as _ROUTINE_DISPATCH
from mcp_hevy.tools.routines import TOOLS as _ROUTINE_TOOLS
from mcp_hevy.tools.user import DISPATCH as _USER_DISPATCH
from mcp_hevy.tools.user import TOOLS as _USER_TOOLS
from mcp_hevy.tools.workouts import DISPATCH as _WORKOUT_DISPATCH
from mcp_hevy.tools.workouts import TOOLS as _WORKOUT_TOOLS

ALL_TOOLS: list[Tool] = (
    _WORKOUT_TOOLS + _ROUTINE_TOOLS + _EXERCISE_TOOLS + _BODY_TOOLS + _USER_TOOLS
)

DISPATCH: dict[str, Callable[[httpx.Client, dict[str, Any]], list[TextContent]]] = {
    **_WORKOUT_DISPATCH,
    **_ROUTINE_DISPATCH,
    **_EXERCISE_DISPATCH,
    **_BODY_DISPATCH,
    **_USER_DISPATCH,
}
