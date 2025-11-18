# CSV to PostgreSQL MCP Server

An MCP (Model Context Protocol) server that loads CSV files into PostgreSQL databases with validation and progress tracking.

## Features

- **CSV Validation**: Validates CSV structure and provides detailed error messages
- **Efficient Loading**: Uses PostgreSQL COPY command for fast bulk loading
- **Progress Tracking**: Shows progress bar for long-running imports
- **Flexible Configuration**: Optional database name (defaults to `csvimports`)
- **Error Reporting**: Exact line numbers and column information for validation errors

## Installation

### From PyPI

```bash
pip install mcp-csv-postgres
```

Or using `uv`:

```bash
uv pip install mcp-csv-postgres
```

### From Source

Clone the repository and install with `uv`:

```bash
git clone https://github.com/raviramadoss/mcp-csv-postgres.git
cd mcp-csv-postgres
uv sync --all-extras
```

## Usage

### As MCP Server

#### Option 1: After installing from PyPI

Add to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "mcp-csv-postgres": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "mcp-csv-postgres",
        "mcp-csv-postgres"
      ]
    }
  }
}
```

#### Option 2: For local development

```json
{
  "mcpServers": {
    "mcp-csv-postgres": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "/path/to/mcp-csv-postgres",
        "--python",
        "3.10",
        "mcp-csv-postgres"
      ]
    }
  }
}
```

Or run directly from command line:

```bash
mcp-csv-postgres
```

### Tool: `load_csv_to_postgres`

Loads a CSV file into PostgreSQL database.

**Parameters:**
- `file_path` (required): Path to the CSV file
- `dbname` (optional): Database name (default: `csvimports`)
- `host` (optional): PostgreSQL host (default: `localhost`)
- `port` (optional): PostgreSQL port (default: `5432`)
- `user` (optional): PostgreSQL user (default: `postgres`)
- `password` (optional): PostgreSQL password
- `table_name` (optional): Table name (derived from filename if not provided)

**Returns:**
- Success message with database name, table name, and rows loaded
- Error message with detailed validation or database errors

## Testing the Server

### Quick Test

Run the test script to see the server in action:

```bash
uv run python test_server.py
```

This will:
1. Create sample CSV files
2. Test loading them into PostgreSQL
3. Test validation error reporting
4. Show detailed output

### Manual Testing with Sample Data

A sample CSV file is provided in `sample_data.csv`. To test manually:

```python
# In Python/IPython
import asyncio
from mcp_csv_postgres.server import call_tool

result = asyncio.run(call_tool(
    "load_csv_to_postgres",
    {"file_path": "sample_data.csv"}
))
print(result[0].text)
```

### Using with MCP Inspector

To test with the MCP Inspector tool:

```bash
npx @modelcontextprotocol/inspector uv run mcp-csv-postgres
```

### VS Code Launch Configurations

The `.vscode/launch.json` includes:
- **Run MCP Server**: Start the server in debug mode
- **Test MCP Server with Sample CSV**: Run the test script
- **Run All Tests**: Execute full test suite
- **Run Specific Test**: Debug a single test file

## Development

### Running Tests

```bash
uv run pytest
```

### Code Coverage

```bash
uv run pytest --cov-report=html
```

Coverage report will be available in `htmlcov/index.html`.

Current coverage: >90%

### Pre-commit Hooks

Pre-commit hooks are configured to run tests before each commit:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Architecture

### Modules

- **validator.py**: CSV validation with detailed error reporting
  - File existence and readability checks
  - CSV structure validation
  - Row consistency validation
  - Automatic dialect detection

- **database.py**: PostgreSQL database operations
  - Connection management
  - Database creation
  - Table creation from CSV headers
  - Row counting

- **loader.py**: CSV loading using COPY command
  - Progress tracking with tqdm
  - Efficient bulk loading
  - Error handling and rollback

- **server.py**: MCP server implementation
  - stdio transport
  - Tool registration
  - Error handling

## Error Handling

The server provides detailed error messages:

- **Validation Errors**: Exact line numbers and description of CSV issues
- **Database Errors**: Connection, permission, and SQL errors
- **File Errors**: Permission, encoding, and file not found errors

## Examples

### Loading a CSV file

```python
{
  "tool": "load_csv_to_postgres",
  "arguments": {
    "file_path": "/path/to/data.csv"
  }
}
```

### With custom database

```python
{
  "tool": "load_csv_to_postgres",
  "arguments": {
    "file_path": "/path/to/data.csv",
    "dbname": "mydb",
    "table_name": "my_table"
  }
}
```

## License

MIT
