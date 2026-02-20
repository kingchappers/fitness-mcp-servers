from collections.abc import Callable

from garminconnect import Garmin  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_garmin.tools.activities import DISPATCH as _ACTIVITY_DISPATCH
from mcp_garmin.tools.activities import TOOLS as _ACTIVITY_TOOLS
from mcp_garmin.tools.body import DISPATCH as _BODY_DISPATCH
from mcp_garmin.tools.body import TOOLS as _BODY_TOOLS
from mcp_garmin.tools.daily import DISPATCH as _DAILY_DISPATCH
from mcp_garmin.tools.daily import TOOLS as _DAILY_TOOLS
from mcp_garmin.tools.goals import DISPATCH as _GOALS_DISPATCH
from mcp_garmin.tools.goals import TOOLS as _GOALS_TOOLS
from mcp_garmin.tools.health import DISPATCH as _HEALTH_DISPATCH
from mcp_garmin.tools.health import TOOLS as _HEALTH_TOOLS
from mcp_garmin.tools.wellness import DISPATCH as _WELLNESS_DISPATCH
from mcp_garmin.tools.wellness import TOOLS as _WELLNESS_TOOLS

ALL_TOOLS: list[Tool] = (
    _DAILY_TOOLS + _ACTIVITY_TOOLS + _HEALTH_TOOLS + _BODY_TOOLS + _GOALS_TOOLS + _WELLNESS_TOOLS
)

DISPATCH: dict[str, Callable[[Garmin, dict[str, str]], list[TextContent]]] = {
    **_DAILY_DISPATCH,
    **_ACTIVITY_DISPATCH,
    **_HEALTH_DISPATCH,
    **_BODY_DISPATCH,
    **_GOALS_DISPATCH,
    **_WELLNESS_DISPATCH,
}
