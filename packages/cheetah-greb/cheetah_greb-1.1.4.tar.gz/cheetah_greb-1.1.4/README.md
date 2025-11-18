# Greb Installation

Getting started with Greb code search is simple and takes just a few minutes.

## Integration Methods

Integrate Greb into your workflow using our REST API service or MCP server for AI assistants. Both provide access to intelligent code search capabilities.

Select your preferred integration method below.

## Steps

### REST API Method

Follow these steps to integrate Greb using our REST API:

#### 1. Get your API key

Sign up for a Greb account and get your API key from the dashboard. Each API key provides access to our intelligent code search capabilities.

#### 2. Install the Python client

Install the Greb Python package to use the REST API service.

```bash
pip install cheetah-greb
```

#### 3. Make your first search request

Initialize the client and search your codebase using natural language queries.

```python
from greb import GrebClient

# Initialize client with your API key
client = GrebClient(api_key='grb_your_api_key_here')

# Search your codebase
results = client.search(
    query='find authentication middleware functions',
    directory='./src',
    file_patterns=['*.js', '*.py'],
    max_results=10
)

# View results
for result in results.results:
    print(f"{result.path}: {result.summary}")
    print(f"Score: {result.score:.3f}")
```

#### 4. API endpoints available

The REST API provides these endpoints:

```bash
# Search code
POST /v1/search

# Health check
GET /health
```

### MCP Server Method

Follow these steps to integrate Greb using our MCP server:

#### 1. Install the Greb package

The MCP server is included in the Greb Python package.

```bash
pip install cheetah-greb
```

#### 2. Configure your MCP client

Add the Greb MCP server to your AI assistant configuration (Claude Desktop, Cline, Cursor, etc.).

```json
{
  "mcpServers": {
    "greb-mcp": {"GREB_API_URL": "https://greb-search.cheetahai.co"
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "greb-mcp",
      "args": [],
      "env": {
        "GREB_API_KEY": "grb_your_api_key_here",
        "GREB_API_URL": "https://greb-search.cheetahai.co"
      }
    }
  }
}
```

#### 3. Start using natural language search

Talk to your AI assistant (Cline, Claude Desktop, etc.) and it will automatically make calls to the MCP server to search your code:

```bash
# Example queries your AI assistant can use:
User: "Search for authentication middleware in the backend directory"
Agent: "[Calls MCP server code_search tool]

User: "Find all API endpoints with file patterns *.js, *.ts"
Agent: [Calls MCP server code_search tool]

User: "Look for database connection setup in ./src"
Agent: [Calls MCP server code_search tool]

User: "Find database configuration files"
Agent: [Calls MCP server code_search tool]
```

#### 4. MCP tools available

The MCP server provides this tool for your AI assistant:

```bash
# code_search(query, directory, file_patterns, max_results)
#   Search code using natural language queries
#   Returns formatted results with code snippets
```

## That's it!

You now have access to intelligent code search through your chosen integration method. Start searching your codebase using natural language queries!