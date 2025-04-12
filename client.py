#!/usr/bin/env python3

import json
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ExchangeRateMCPClient:
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            port = os.getenv("PORT", "3000")
            self.base_url = f"http://localhost:{port}"
        else:
            self.base_url = base_url
    
    def get_exchange_rates(self, base_currency: str = "USD", symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get exchange rates from the MCP server
        
        Args:
            base_currency: Base currency code (e.g., "USD", "EUR")
            symbols: List of currency codes to get rates for
            
        Returns:
            Dictionary containing exchange rate data
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "callTool",
                "params": {
                    "name": "exchange-rates",
                    "parameters": {
                        "base": base_currency
                    }
                }
            }
            
            if symbols:
                payload["params"]["parameters"]["symbols"] = symbols
                
            response = requests.post(f"{self.base_url}/tools", json=payload)
            response.raise_for_status()
            
            result = response.json().get("result", {})
            return result
        except Exception as e:
            print(f"Error fetching exchange rates: {e}")
            if hasattr(e, "response") and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            raise

def main():
    client = ExchangeRateMCPClient()
    port = os.getenv("PORT", "3000")
    
    print(f"Fetching exchange rates from MCP server at http://localhost:{port}...")
    try:
        result = client.get_exchange_rates("EUR", ["USD", "GBP", "JPY", "CAD", "AUD"])
        
        print("\nExchange Rate MCP Response:")
        print(json.dumps(result, indent=2))
        
        # Extract and display the rates in a readable format
        if "content" in result and "rates" in result["content"]:
            print("\nCurrent Exchange Rates:")
            print(f"Base Currency: {result['content']['base']}")
            print(f"Date: {result['content']['date']}")
            print("Rates:")
            for currency, rate in result["content"]["rates"].items():
                print(f"  {currency}: {rate}")
    except Exception as e:
        print(f"Test failed: {e}")
        return
        
    print("\nTest completed successfully")

if __name__ == "__main__":
    main()
