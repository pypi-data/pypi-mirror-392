#!/usr/bin/env python3
"""
BurpSuite MCP Server - Model Context Protocol compatible server
Provides BurpSuite proxy, scanner, and logging functionality through MCP protocol
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional
import requests
import os
from dotenv import load_dotenv
import urllib3
from urllib.parse import urlparse
import re
from datetime import datetime
from collections import defaultdict

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# BurpSuite Configuration
BURP_PROXY_HOST = os.getenv("BURP_PROXY_HOST", "127.0.0.1")
BURP_PROXY_PORT = int(os.getenv("BURP_PROXY_PORT", "8080"))
BURP_PROXY_URL = f"http://{BURP_PROXY_HOST}:{BURP_PROXY_PORT}"

# Global storage for scans and logs
active_scans = {}
http_logs = []
scan_counter = 0

class MCPServer:
    def __init__(self):
        self.session = requests.Session()
        self.session.proxies = {
            "http": BURP_PROXY_URL,
            "https": BURP_PROXY_URL
        }
        self.session.verify = False

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                return await self.initialize(params)
            elif method == "tools/list":
                return await self.list_tools()
            elif method == "tools/call":
                return await self.call_tool(params)
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP server"""
        return {
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "burpsuite-mcp-server",
                    "version": "1.0.0"
                }
            }
        }

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        tools = [
            {
                "name": "proxy_request",
                "description": "Send HTTP request through BurpSuite proxy",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target URL"},
                        "method": {"type": "string", "description": "HTTP method (GET, POST, etc.)", "default": "GET"},
                        "headers": {"type": "object", "description": "HTTP headers"},
                        "data": {"type": "string", "description": "Request body data"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "start_scan",
                "description": "Start vulnerability scan on target URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target URL to scan"},
                        "scan_type": {"type": "string", "description": "Type of scan (basic, full)", "default": "basic"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "get_scan_status",
                "description": "Get status of running scan",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scan_id": {"type": "string", "description": "Scan ID"}
                    },
                    "required": ["scan_id"]
                }
            },
            {
                "name": "stop_scan",
                "description": "Stop running scan",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scan_id": {"type": "string", "description": "Scan ID"}
                    },
                    "required": ["scan_id"]
                }
            },
            {
                "name": "get_http_logs",
                "description": "Get HTTP request/response logs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Maximum number of logs to return", "default": 10},
                        "filter_url": {"type": "string", "description": "Filter logs by URL pattern"}
                    }
                }
            },
            {
                "name": "analyze_vulnerabilities",
                "description": "Analyze response for common vulnerabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target URL"},
                        "response_text": {"type": "string", "description": "Response content to analyze"}
                    },
                    "required": ["url", "response_text"]
                }
            }
        ]
        
        return {"result": {"tools": tools}}

    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "proxy_request":
                return await self.proxy_request(arguments)
            elif tool_name == "start_scan":
                return await self.start_scan(arguments)
            elif tool_name == "get_scan_status":
                return await self.get_scan_status(arguments)
            elif tool_name == "stop_scan":
                return await self.stop_scan(arguments)
            elif tool_name == "get_http_logs":
                return await self.get_http_logs(arguments)
            elif tool_name == "analyze_vulnerabilities":
                return await self.analyze_vulnerabilities(arguments)
            else:
                return {
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Tool execution error: {str(e)}"
                }
            }

    async def proxy_request(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send HTTP request through BurpSuite proxy"""
        url = args.get("url")
        method = args.get("method", "GET").upper()
        headers = args.get("headers", {})
        data = args.get("data")

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=30
            )
            
            # Log the request/response
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "response_size": len(response.content),
                "headers": dict(response.headers)
            }
            http_logs.append(log_entry)
            
            return {
                "result": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.text[:1000] + "..." if len(response.text) > 1000 else response.text,
                    "size": len(response.content)
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Request failed: {str(e)}"
                }
            }

    async def start_scan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start vulnerability scan"""
        global scan_counter
        url = args.get("url")
        scan_type = args.get("scan_type", "basic")
        
        scan_counter += 1
        scan_id = f"scan_{scan_counter}"
        
        # Simulate scan start
        active_scans[scan_id] = {
            "url": url,
            "scan_type": scan_type,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "vulnerabilities": []
        }
        
        # Perform basic vulnerability checks
        try:
            response = self.session.get(url, timeout=10)
            vulnerabilities = self._check_vulnerabilities(url, response.text)
            active_scans[scan_id]["vulnerabilities"] = vulnerabilities
            active_scans[scan_id]["status"] = "completed"
        except Exception as e:
            active_scans[scan_id]["status"] = "failed"
            active_scans[scan_id]["error"] = str(e)
        
        return {
            "result": {
                "scan_id": scan_id,
                "status": "started",
                "url": url,
                "scan_type": scan_type
            }
        }

    async def get_scan_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get scan status"""
        scan_id = args.get("scan_id")
        
        if scan_id not in active_scans:
            return {
                "error": {
                    "code": -32602,
                    "message": "Scan not found"
                }
            }
        
        return {"result": active_scans[scan_id]}

    async def stop_scan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Stop scan"""
        scan_id = args.get("scan_id")
        
        if scan_id not in active_scans:
            return {
                "error": {
                    "code": -32602,
                    "message": "Scan not found"
                }
            }
        
        active_scans[scan_id]["status"] = "stopped"
        return {"result": {"message": f"Scan {scan_id} stopped"}}

    async def get_http_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get HTTP logs"""
        limit = args.get("limit", 10)
        filter_url = args.get("filter_url")
        
        logs = http_logs[-limit:] if not filter_url else [
            log for log in http_logs[-100:] 
            if filter_url.lower() in log["url"].lower()
        ][:limit]
        
        return {"result": {"logs": logs, "total": len(logs)}}

    async def analyze_vulnerabilities(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze vulnerabilities in response"""
        url = args.get("url")
        response_text = args.get("response_text")
        
        vulnerabilities = self._check_vulnerabilities(url, response_text)
        
        return {
            "result": {
                "url": url,
                "vulnerabilities": vulnerabilities,
                "total_found": len(vulnerabilities)
            }
        }

    def _check_vulnerabilities(self, url: str, response_text: str) -> List[Dict[str, Any]]:
        """Check for common vulnerabilities"""
        vulnerabilities = []
        
        # XSS Detection
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                vulnerabilities.append({
                    "type": "XSS",
                    "severity": "High",
                    "description": "Potential Cross-Site Scripting vulnerability detected",
                    "pattern": pattern
                })
                break
        
        # SQL Injection indicators
        sql_errors = [
            "sql syntax",
            "mysql_fetch",
            "ora-[0-9]+",
            "microsoft ole db provider",
            "sqlite_master"
        ]
        
        for error in sql_errors:
            if error.lower() in response_text.lower():
                vulnerabilities.append({
                    "type": "SQL_INJECTION",
                    "severity": "Critical",
                    "description": "Potential SQL Injection vulnerability detected",
                    "indicator": error
                })
                break
        
        # Directory traversal
        if "../" in response_text or "..\\/" in response_text:
            vulnerabilities.append({
                "type": "DIRECTORY_TRAVERSAL",
                "severity": "Medium",
                "description": "Potential Directory Traversal vulnerability detected"
            })
        
        # Information disclosure
        info_patterns = [
            r'password\s*[:=]\s*["\']?[^"\'\s]+',
            r'api[_-]?key\s*[:=]\s*["\']?[^"\'\s]+',
            r'secret\s*[:=]\s*["\']?[^"\'\s]+'
        ]
        
        for pattern in info_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                vulnerabilities.append({
                    "type": "INFORMATION_DISCLOSURE",
                    "severity": "Medium",
                    "description": "Potential sensitive information disclosure detected"
                })
                break
        
        return vulnerabilities

async def main():
    """Main MCP server loop"""
    server = MCPServer()
    
    # Read from stdin and write to stdout for MCP protocol
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            # Add request ID if present
            if "id" in request:
                response["id"] = request["id"]
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            error_response = {
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            error_response = {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
