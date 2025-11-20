"""MCP Server.

A FastMCP-based server providing prompts, resources, and tools for your AI assistants.
"""

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

try:
    from slash_commands.__version__ import __version__
except (ImportError, AttributeError):
    # Fallback for when installed as a package or circular import during development
    try:
        from importlib.metadata import version

        __version__ = version("slash-man")
    except Exception:
        # Final fallback: read from pyproject.toml directly
        import tomllib
        from pathlib import Path

        try:
            # Try to find pyproject.toml relative to this file
            init_file_path = Path(__file__).parent
            repo_root = init_file_path.parent
            pyproject_path = repo_root / "pyproject.toml"
            if pyproject_path.exists():
                with pyproject_path.open("rb") as f:
                    data = tomllib.load(f)
                    __version__ = data["project"]["version"]
            else:
                __version__ = "unknown"
        except Exception:
            __version__ = "unknown"

from .config import config
from .prompts_loader import register_prompts


def create_app() -> FastMCP:
    """Create and configure the FastMCP application.

    Returns:
        Configured FastMCP server instance
    """
    # Initialize FastMCP server
    mcp = FastMCP(name="slash-man-mcp")

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")

    # Load prompts from the prompts directory and register them
    register_prompts(mcp, config.prompts_dir)

    @mcp.tool(name="basic-example", description="Return a static message for testing.")
    def basic_example_tool() -> str:
        """Basic example tool used to verify MCP tool registration."""

        return "Basic example tool invoked successfully."

    # TODO: Register resources (Task 2.1)
    # TODO: Register tools (Task 5.1)
    # TODO: Setup notifications (Task 5.2)
    # TODO: Setup sampling (Task 5.3)
    # TODO: Setup logging (Task 5.4)

    return mcp
