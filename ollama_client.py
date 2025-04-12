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

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def generate_response(self, model: str, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate a response from Ollama
        
        Args:
            model: Model name (e.g., "gemma3:27b")
            prompt: Text prompt to send to the model
            options: Additional options for the model
            
        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            if options:
                payload.update(options)
                
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            raise

def main():
    port = os.getenv("PORT", "3000")
    mcp_client = ExchangeRateMCPClient()
    ollama_client = OllamaClient()
    model = "gemma3:27b"
    
    try:
        print(f"Fetching current exchange rates from http://localhost:{port}...")
        exchange_rate_data = mcp_client.get_exchange_rates("USD", ["EUR", "GBP", "JPY", "CAD", "AUD"])
        
        # Parse the exchange rate data
        rates_info = exchange_rate_data["content"]
        formatted_rates = "\n".join([f"{currency}: {rate}" for currency, rate in rates_info["rates"].items()])
        
        # Create a prompt with the exchange rate data
        prompt = f"""
You are a helpful financial assistant with access to the latest exchange rates.

Current exchange rates (base: {rates_info['base']}, date: {rates_info['date']}):
{formatted_rates}

Based on these rates, if I have 1000 USD, how much would that be in EUR and GBP?
Please show your calculations and provide a brief explanation of the current exchange rate situation.
"""

        print("Sending prompt to Ollama with gemma3:27b model...")
        response = ollama_client.generate_response(model, prompt)
        
        print("\n--- Gemma 3 Response ---\n")
        print(response)
        
        # Save the conversation to a file for reference
        conversation = f"""
PROMPT:
{prompt}

RESPONSE:
{response}
"""
        with open("ollama-mcp-conversation.txt", "w") as f:
            f.write(conversation)
        print("\nConversation saved to ollama-mcp-conversation.txt")
        
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
