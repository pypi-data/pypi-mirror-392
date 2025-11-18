# MySQL MCP Server

A modern MySQL Model Context Protocol (MCP) server built with FastMCP.

## Features

- Execute SQL queries via MCP tools
- Browse database tables and structure via MCP resources
- SSL certificate support
- Connection pooling and error handling

## Configuration

### Command Line Arguments

#### Required Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--user` | MySQL username | **(required)** |
| `--password` | MySQL password | **(required)** |
| `--database` | MySQL database name | **(required)** |

#### Database Connection (Optional)
| Argument | Description | Default |
|----------|-------------|---------|
| `--host` | MySQL server host | `localhost` |
| `--port` | MySQL server port | `3306` |

#### SSL Configuration (Optional)
| Argument | Description | Default |
|----------|-------------|---------|
| `--ssl-ca` | Path to SSL CA certificate file | *(none - SSL auto-negotiated)* |
| `--ssl-cert` | Path to SSL client certificate file | *(none)* |
| `--ssl-key` | Path to SSL client private key file | *(none)* |
| `--ssl-disabled` | Disable SSL connection entirely | `false` |

**Note:** If `--ssl-cert` is provided, `--ssl-key` must also be provided, and vice versa.

#### Advanced Options (Optional)
| Argument | Description | Default |
|----------|-------------|---------|
| `--charset` | Character set for the connection | `utf8mb4` |
| `--collation` | Collation for the connection | `utf8mb4_unicode_ci` |
| `--sql-mode` | MySQL SQL mode | `TRADITIONAL` |

## Usage

#### Simple Usage (Streamable HTTP Default)

Launch the server:

```bash
uvx mysql-mcp-zag \
  --host localhost \
  --port 3306 \
  --user your_user \
  --password your_password \
  --database your_database
```

This starts a Streamable-HTTP MCP endpoint listening on `http://127.0.0.1:8000/mcp`. Configure your MCP client accordingly, e.g. in Codex:

```json
{
  "mcpServers": {
    "mysql": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

If you need to reach a remote MySQL instance, pass the appropriate database host/port/SSL flags—transport stays Streamable-HTTP so clients remain spec-compliant.

## Available Tools

- `execute_sql`: Execute SQL queries

## Available Resources

- `mysql://tables`: List all tables
- `mysql://tables/{table}`: Describe table structure


## Requirements

- Python 3.13+
- MySQL server
- uvx (for installation and usage)

---

Created by Michael Zag, Michael@MichaelZag.com
