from collections.abc import Callable

import myfitnesspal  # type: ignore[import-untyped]
from mcp.types import TextContent, Tool

from mcp_myfitnesspal.tools.body import DISPATCH as _BODY_DISPATCH
from mcp_myfitnesspal.tools.body import TOOLS as _BODY_TOOLS
from mcp_myfitnesspal.tools.nutrition import DISPATCH as _NUTRITION_DISPATCH
from mcp_myfitnesspal.tools.nutrition import TOOLS as _NUTRITION_TOOLS

ALL_TOOLS: list[Tool] = _NUTRITION_TOOLS + _BODY_TOOLS

DISPATCH: dict[str, Callable[[myfitnesspal.Client, dict[str, str]], list[TextContent]]] = {
    **_NUTRITION_DISPATCH,
    **_BODY_DISPATCH,
}
