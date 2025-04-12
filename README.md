# Exchange Rate MCP Server (Python)

This is a Python implementation of a Model Context Protocol (MCP) server that provides current exchange rates from a reliable source.

## Overview

This server implements the Model Context Protocol to provide real-time exchange rate data. It can be used by AI models to get up-to-date currency exchange information.

## Features

- Provides current exchange rates for various currencies
- Configurable base currency (defaults to USD)
- Uses the exchangerate.host API as a data source
- Includes client examples and Ollama integration

## Installation

```bash
# Clone the repository
git clone git@github.com:devshark/exchange-rate-mcp.git
cd exchange-rate-mcp

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the example environment file and edit as needed
cp .env.example .env
```

## Configuration

Edit the `.env` file to configure:

- `PORT`: The port on which the server will run (default: 3000)
- `EXCHANGE_API_KEY`: Your API key for the exchange rate service (optional for some providers)

## Usage

### Starting the Server

```bash
python server.py
```

The server will start on the port specified in your `.env` file (default: 3000).

### Testing with the Client

```bash
python client.py
```

This will send a request to the MCP server and display the response.

### Testing with Ollama Integration

First, make sure you have Ollama installed and the gemma3:27b model downloaded:

```bash
ollama pull gemma3:27b
```

Then run the Ollama client:

```bash
python ollama_client.py
```

This will:
1. Fetch exchange rates from the MCP server
2. Format them into a prompt
3. Send the prompt to Ollama
4. Display and save the response

## API

The server exposes an MCP endpoint that accepts JSON-RPC 2.0 requests with the following methods:

### listTools

Lists available tools on the server.

Example request:
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "listTools",
  "params": {}
}
```

### callTool

Calls a specific tool with parameters.

Example request:
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "callTool",
  "params": {
    "name": "exchange-rates",
    "parameters": {
      "base": "EUR",
      "symbols": ["USD", "GBP", "JPY"]
    }
  }
}
```

Example response:
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "content": {
      "base": "EUR",
      "date": "2025-04-12",
      "rates": {
        "USD": 1.0923,
        "GBP": 0.8578,
        "JPY": 163.27
      }
    },
    "metadata": {
      "source": "exchange-rate-mcp",
      "timestamp": "2025-04-12T12:25:30.123Z",
      "baseCurrency": "EUR",
      "symbols": "USD,GBP,JPY"
    }
  }
}
```

## License

ISC
