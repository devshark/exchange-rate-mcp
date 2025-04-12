#!/usr/bin/env python3

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("exchange-rate-mcp")

# Create FastAPI app
app = FastAPI(
    title="Exchange Rate MCP Server",
    description="Model Context Protocol server for exchange rates",
    version="0.1.0",
)

# Models
class ExchangeRateParameters(BaseModel):
    base: Optional[str] = Field(default="USD", description="Base currency code")
    symbols: Optional[List[str]] = Field(default=None, description="List of currency symbols to get rates for")

class JsonRpcRequest(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: str
    method: str
    params: Dict[str, Any]

class JsonRpcResponse(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class ListToolsResponse(BaseModel):
    tools: List[Dict[str, Any]]

class MCPMetadata(BaseModel):
    source: str
    timestamp: str
    baseCurrency: str
    symbols: Optional[str] = None

class MCPResponse(BaseModel):
    content: Dict[str, Any]
    metadata: MCPMetadata

# Exchange Rate Provider
class ExchangeRateProvider:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.exchangerate.host/latest"
    
    async def get_current_rates(self, base: str = "USD", symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        params = {"base": base}
        
        if self.api_key:
            params["access_key"] = self.api_key
            
        if symbols:
            params["symbols"] = ",".join(symbols)
            
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch exchange rates: {str(e)}")

# Create exchange rate provider
exchange_rate_provider = ExchangeRateProvider(api_key=os.getenv("EXCHANGE_API_KEY"))

# MCP Tool definitions
exchange_rate_tool = {
    "name": "exchange-rates",
    "description": "Get the latest exchange rates",
    "parameters": {
        "type": "object",
        "properties": {
            "base": {
                "type": "string",
                "description": "The base currency",
                "default": "USD"
            },
            "symbols": {
                "type": "array",
                "description": "The target currencies",
                "items": {
                    "type": "string"
                }
            }
        }
    }
}

# Routes
@app.get("/")
async def root():
    return {"message": "Exchange Rate MCP Server", "version": "0.1.0"}

@app.post("/tools")
async def handle_tools_request(request: JsonRpcRequest):
    try:
        if request.method == "listTools":
            return JsonRpcResponse(
                jsonrpc="2.0",
                id=request.id,
                result={"tools": [exchange_rate_tool]}
            )
        elif request.method == "callTool":
            tool_name = request.params.get("name")
            if tool_name != "exchange-rates":
                return JsonRpcResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                )
                
            parameters = request.params.get("parameters", {})
            base_currency = parameters.get("base", "USD")
            symbols = parameters.get("symbols")
            
            rates_data = await exchange_rate_provider.get_current_rates(base_currency, symbols)
            
            response = MCPResponse(
                content={
                    "base": rates_data["base"],
                    "date": rates_data["date"],
                    "rates": rates_data["rates"]
                },
                metadata=MCPMetadata(
                    source="exchange-rate-mcp",
                    timestamp=datetime.now().isoformat(),
                    baseCurrency=base_currency,
                    symbols=",".join(symbols) if symbols else None
                )
            )
            
            return JsonRpcResponse(
                jsonrpc="2.0",
                id=request.id,
                result=response.dict()
            )
        else:
            return JsonRpcResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {request.method}"
                }
            )
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return JsonRpcResponse(
            jsonrpc="2.0",
            id=request.id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    print(f"Starting Exchange Rate MCP Server on port {port}...")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
