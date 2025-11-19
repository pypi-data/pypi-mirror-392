import sys
import contextlib
import platform

from typing import Annotated, Literal
from collections.abc import AsyncIterator

import uvicorn

from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from chipiq import simiq
from chipiq import __version__ as chipiq_version

from simiq_mcp import __version__

# Initialize FastMCP server
mcp = FastMCP("SimIQ-MCP-Server")

@mcp.tool()
async def analyze_simulation_waveform_file(
    uri_or_filepath: Annotated[str, 
        "A 'http:', 'https:', 'file:' or 'data:' URI or file path."] = "",
    report_type: Annotated[
        Literal["user_manual", "vcd", "modules", "signals", "info"],
        "Type of report to generate: "
        "- 'user_manual': Show detailed help and example usage information, "
        "- 'vcd': Show signal value changes, "
        #"- 'trend': Summarize signal trends, "
        #"- 'wave': Show signal waveform diagrams, "
        "- 'modules': List module names, "
        "- 'signals': List signal names, "
        "- 'info': Show general information for the waveform file. "
        "Default: 'user_manual'."
        ] = "user_manual",
    from_timestamp: Annotated[int, 
        "First timestamp to include in report. Default: 0"] = 0,
    signal_names: Annotated[list[str], 
        "List with signal names "
        "(as '<module>.<submodule>.<signal>' with '**' and '*' wildcards) "
        "to include in report. Default: signals on top-level only."] = [".*"],
) -> str:
    """ 
    Analyze a VCD-file described by an http:, https:, file: or data: URI. 
    Call without parameters (use: 'analyze_vcd_file()') to show detailed 
    help and example usage information.
    """
    return simiq(
        uri_or_filepath=uri_or_filepath, 
        report_type=report_type,
        from_timestamp=from_timestamp, 
        signal_names=signal_names,
    )

def create_starlette_app(
    mcp_server: Server, 
    *, 
    debug: bool = False
) -> Starlette:
    sse = SseServerTransport("/messages/")
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            print("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                print("Application shutting down...")

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/mcp", app=handle_streamable_http),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        lifespan=lifespan,
    )

def main():
    import argparse

    mcp_server = mcp._mcp_server

    parser = argparse.ArgumentParser(description="Run SimIQ MCP server")

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run the server with Streamable HTTP and SSE transport rather than STDIO (default: False)",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="(Deprecated) An alias for --http (default: False)",
    )
    parser.add_argument(
        "--host", default=None, help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Port to listen on (default: 3001)"
    )
    args = parser.parse_args()

    if args.version:
        print(f"SimIQ-MCP: {__version__}")
        print(f"ChipIQ: {chipiq_version}")
        print(f"Python: {platform.python_version()}")
        print(f"Platform: {platform.platform()}")
        sys.exit(0)

    use_http = args.http or args.sse

    if not use_http and (args.host or args.port):
        parser.error(
            "Host and port arguments are only valid when using streamable HTTP or SSE transport (see: --http)."
        )
        sys.exit(1)

    if use_http:
        starlette_app = create_starlette_app(mcp_server, debug=True)
        uvicorn.run(
            starlette_app,
            host=args.host if args.host else "127.0.0.1",
            port=args.port if args.port else 3001,
        )
    else:
        mcp.run()

if __name__ == "__main__":
    main()
