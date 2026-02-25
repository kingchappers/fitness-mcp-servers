from __future__ import annotations

import asyncio
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_myfitnesspal import tools
from mcp_myfitnesspal.client import get_client
from mcp_myfitnesspal.exceptions import MFPShapeError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server: Server = Server("mcp-myfitnesspal")


@server.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
async def list_tools() -> list[Tool]:
    return tools.ALL_TOOLS


@server.call_tool()  # type: ignore[untyped-decorator]
async def call_tool(name: str, arguments: dict[str, str]) -> list[TextContent]:
    logger.info("Tool called: %s", name)
    try:
        client = get_client()
        handler = tools.DISPATCH.get(name)
        if handler is None:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        return handler(client, arguments)
    except RuntimeError as exc:
        logger.error("Auth error in tool %s: %s", name, exc)
        return [TextContent(type="text", text=str(exc))]
    except MFPShapeError as exc:
        logger.error("MFP shape error in tool %s: %s", name, exc)
        return [TextContent(type="text", text=str(exc))]
    except ValueError as exc:
        logger.error("Validation error in tool %s: %s", name, exc)
        return [TextContent(type="text", text=f"Invalid argument: {exc}")]
    except Exception as exc:
        logger.error("Unexpected error in tool %s: %s", name, exc, exc_info=True)
        return [TextContent(type="text", text=f"Unexpected error: {exc}")]


async def _run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
