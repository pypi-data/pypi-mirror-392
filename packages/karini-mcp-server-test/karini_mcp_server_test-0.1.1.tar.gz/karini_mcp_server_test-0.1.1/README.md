# Karini MCP Server

MCP (Model Context Protocol) server for integrating Karini AI copilots and webhook recipes with Claude Desktop and other MCP clients.

## Features

- 🤖 **AI Copilot Integration** - Ask questions and get AI-powered responses from your Karini copilots
- 📄 **Document Processing** - Process documents stored in S3 through copilots and webhooks
- 🔗 **Webhook Recipes** - Trigger asynchronous data processing workflows
- 📊 **Status Tracking** - Monitor webhook execution status and results

## Installation

### Via uvx (Recommended)
```bash
uvx karini-mcp-server
```

### Via pip
```bash
pip install karini-mcp-server
```

## Configuration

### Claude Desktop Setup

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Full Configuration (All Features)
```json
{
  "mcpServers": {
    "karini-mcp-server": {
      "command": "uvx",
      "args": ["karini-mcp-server@latest"],
      "env": {
        "KARINI_API_BASE": "https://app.karini.ai",
        "KARINI_COPILOT_ID": "your-copilot-id",
        "KARINI_API_KEY": "your-copilot-api-key",
        "WEBHOOK_API_KEY": "your-webhook-api-key",
        "WEBHOOK_RECIPE_ID": "your-webhook-recipe-id"
      }
    }
  }
}
```

#### Copilot Only Configuration
```json
{
  "mcpServers": {
    "karini-mcp-server": {
      "command": "uvx",
      "args": ["karini-mcp-server@latest"],
      "env": {
        "KARINI_API_BASE": "https://app.karini.ai",
        "KARINI_COPILOT_ID": "your-copilot-id",
        "KARINI_API_KEY": "your-copilot-api-key"
      }
    }
  }
}
```

#### Webhook Only Configuration
```json
{
  "mcpServers": {
    "karini-mcp-server": {
      "command": "uvx",
      "args": ["karini-mcp-server@latest"],
      "env": {
        "KARINI_API_BASE": "https://app.karini.ai",
        "WEBHOOK_API_KEY": "your-webhook-api-key",
        "WEBHOOK_RECIPE_ID": "your-webhook-recipe-id"
      }
    }
  }
}
```

**Note:** Only tools with valid configuration will be available. If webhook credentials are not provided, only copilot tools will appear.

## Environment Variables

| Variable | Required For | Description |
|----------|-------------|-------------|
| `KARINI_API_BASE` | All | Base URL for Karini API (e.g., `https://app.karini.ai`) |
| `KARINI_COPILOT_ID` | Copilot Tools | Your copilot's unique identifier |
| `KARINI_API_KEY` | Copilot Tools | API key for copilot authentication |
| `KARINI_WEBHOOK_API_KEY` | Webhook Tools | API key for webhook authentication |
| `KARINI_WEBHOOK_RECIPE_ID` | Webhook Tools | Webhook recipe identifier |

## Available Tools

### Copilot Tools

#### `ask_karini_copilot`

Ask questions to your Karini AI copilot and receive intelligent responses.

**Parameters:**
- `question` (string, required): The question or query to ask
- `files` (list, optional): S3 file paths to include in the query
  - Example: `["s3://bucket/document.pdf", "s3://bucket/data.txt"]`

### Webhook Tools

#### `invoke_webhook_recipe`

Trigger a webhook recipe for asynchronous data processing.

**Parameters:**
- `question` (string, optional): Input message or query
- `files` (list, optional): S3 file paths to process (content type auto-detected)
  - Example: `["s3://bucket/invoice.pdf", "s3://bucket/receipt.jpg"]`
- `metadata` (dict, optional): Additional context as key-value pairs
  - Example: `{"user_id": "123", "priority": "high", "source": "email"}`

**Returns:** JSON with `request_id` for status tracking

#### `get_webhook_status`

Check the status of webhook recipe executions.

**Parameters:**
- `request_id` (string, optional): Specific request ID to check
- `limit` (integer, optional): Number of recent requests to return (default: 5)


## Development

### Local Testing
```bash
# Clone repository
git clone https://github.com/yourusername/karini-mcp-server.git
cd karini-mcp-server

# Install dependencies
pip install -e .

# Run locally
python -m src.main
```

### Project Structure
```
karini-mcp-server/
├── src/
│   ├── main.py              # Entry point
│   ├── server.py            # MCP server setup
│   ├── services/
│   │   ├── config.py        # Configuration management
│   │   └── client.py        # Karini API client
│   └── tools/
│       └── tools.py         # Tool definitions
├── pyproject.toml
└── README.md
```