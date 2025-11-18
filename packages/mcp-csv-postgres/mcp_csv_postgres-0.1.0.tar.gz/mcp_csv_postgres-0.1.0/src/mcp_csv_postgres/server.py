"""MCP server for CSV to PostgreSQL loading."""

import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .loader import load_csv
from .validator import ValidationError
from .database import DatabaseError


app = Server("csv-postgres-loader")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools.

    Returns:
        List of available MCP tools
    """
    return [
        Tool(
            name="load_csv_to_postgres",
            description="Load a CSV file into PostgreSQL database. Validates CSV structure and provides detailed error messages. Uses PostgreSQL COPY for efficient loading of large files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the CSV file to load"
                    },
                    "dbname": {
                        "type": "string",
                        "description": "Database name (optional, default: csvimports)",
                        "default": "csvimports"
                    },
                    "host": {
                        "type": "string",
                        "description": "PostgreSQL host (optional, default: localhost)",
                        "default": "localhost"
                    },
                    "port": {
                        "type": "integer",
                        "description": "PostgreSQL port (optional, default: 5432)",
                        "default": 5432
                    },
                    "user": {
                        "type": "string",
                        "description": "PostgreSQL user (optional, default: postgres)",
                        "default": "postgres"
                    },
                    "password": {
                        "type": "string",
                        "description": "PostgreSQL password (optional)"
                    },
                    "table_name": {
                        "type": "string",
                        "description": "Table name (optional, derived from filename if not provided)"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        List of text content with results
    """
    if name != "load_csv_to_postgres":
        raise ValueError(f"Unknown tool: {name}")

    try:
        result = load_csv(
            file_path=arguments["file_path"],
            dbname=arguments.get("dbname", "csvimports"),
            host=arguments.get("host", "localhost"),
            port=arguments.get("port", 5432),
            user=arguments.get("user", "postgres"),
            password=arguments.get("password"),
            table_name=arguments.get("table_name"),
            show_progress=False
        )

        message = (
            f"Successfully loaded CSV to PostgreSQL\n"
            f"Database: {result['database']}\n"
            f"Table: {result['table_name']}\n"
            f"Rows loaded: {result['rows_loaded']}"
        )

        return [TextContent(type="text", text=message)]

    except ValidationError as e:
        error_message = f"CSV Validation Error: {str(e)}"
        return [TextContent(type="text", text=error_message)]

    except DatabaseError as e:
        error_message = f"Database Error: {str(e)}"
        return [TextContent(type="text", text=error_message)]

    except Exception as e:
        error_message = f"Unexpected Error: {str(e)}"
        return [TextContent(type="text", text=error_message)]


async def run_server():
    """Run the MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Main entry point for the server."""
    import asyncio
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
