#!/usr/bin/env python3
"""Test script for the MCP Weather Server"""

import json
import asyncio
import subprocess
import sys

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    # Start the server
    server_process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Test 1: List tools
    list_request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    })
    
    print("🔍 Testing: tools/list")
    server_process.stdin.write(list_request + '\n')
    server_process.stdin.flush()
    
    # Read response
    response = await asyncio.get_event_loop().run_in_executor(
        None, server_process.stdout.readline
    )
    
    print(f"Response: {response}")
    
    # Cleanup
    server_process.terminate()
    server_process.wait()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
