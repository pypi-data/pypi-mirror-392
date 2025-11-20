# Fanvue MCP Server

A Model Context Protocol (MCP) server for the Fanvue API.

## Installation

```bash
pip install fanvue-mcp
```

Or use with `uvx` (no installation required):

```bash
uvx fanvue-mcp
```

## Usage

To run the server, you need to provide your Fanvue OAuth credentials. You can obtain these by creating an application in the [Fanvue Developer Portal](https://www.fanvue.com/developers/apps).

### Running the Server

```bash
export FANVUE_CLIENT_ID="your_client_id"
export FANVUE_CLIENT_SECRET="your_client_secret"

# Run the server
fanvue-mcp
```

The server will start at `http://0.0.0.0:8080` with the following endpoints:
- **MCP Endpoint**: `http://localhost:8080/mcp`
- **SSE Endpoint**: `http://localhost:8080/sse`
- **Health Check**: `http://localhost:8080/health`

## Connecting to MCP Clients

### Cursor

1. Open Cursor Settings (`Cmd/Ctrl + Shift + J` or Settings UI).
2. Navigate to **Features** > **MCP**.
3. Edit your MCP settings JSON and add:

```json
{
  "mcpServers": {
    "fanvue": {
      "command": "uvx",
      "args": ["fanvue-mcp"],
      "env": {
        "FANVUE_CLIENT_ID": "your_client_id",
        "FANVUE_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

Cursor will automatically start and manage the server process.

### Claude Code (VS Code Extension)

1. Open VS Code Settings (`Cmd/Ctrl + ,`).
2. Search for "MCP" or navigate to **Extensions** > **Claude Code**.
3. Edit the MCP configuration (usually in `settings.json`):

```json
{
  "claude.mcpServers": {
    "fanvue": {
      "command": "uvx",
      "args": ["fanvue-mcp"],
      "env": {
        "FANVUE_CLIENT_ID": "your_client_id",
        "FANVUE_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

The extension will manage the server lifecycle automatically.

### Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fanvue": {
      "command": "uvx",
      "args": ["fanvue-mcp"],
      "env": {
        "FANVUE_CLIENT_ID": "your_client_id",
        "FANVUE_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

Restart Claude Desktop after saving the configuration.

## Environment Variables

- `FANVUE_CLIENT_ID`: Your Fanvue OAuth Client ID (Required)
- `FANVUE_CLIENT_SECRET`: Your Fanvue OAuth Client Secret (Required)
- `MCP_SERVER_PORT`: Port to run the server on (Default: 8080)
- `MCP_SERVER_HOST`: Host to bind to (Default: 0.0.0.0)
- `MCP_SERVER_URL`: Public URL of the server (Default: http://localhost:8080) - used for OAuth redirects
- `FANVUE_API_URL`: Fanvue API URL (Default: https://api.fanvue.com)
- `FANVUE_AUTH_URL`: Fanvue Auth URL (Default: https://auth.fanvue.com)
- `DEBUG`: Enable debug logging (Default: false)

## Development

To develop locally:

1. Clone the repository
2. Install dependencies: `uv sync`
3. Run the server: `uv run fanvue-mcp`
