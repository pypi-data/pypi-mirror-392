#!/usr/bin/env python3
"""Syncline MCP Server - Main implementation"""

import asyncio
import os
import sys
from typing import Any
from urllib.parse import quote

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

VERSION = "1.0.19"

# Syncline API configuration
SYNCLINE_API_URL = os.getenv("SYNCLINE_API_URL", "https://api.syncline.run")
SYNCLINE_API_KEY = os.getenv("SYNCLINE_API_KEY")

if not SYNCLINE_API_KEY:
    print("Error: SYNCLINE_API_KEY environment variable is required", file=sys.stderr)
    sys.exit(1)

# Meeting contexts supported by Syncline
MEETING_CONTEXTS = [
    "warm_intro", "cold_outreach", "investor_call", "client_demo",
    "team_standup", "one_on_one", "interview", "sales_call",
    "strategy_session", "brainstorm", "review", "casual_chat", "urgent"
]

# Create MCP server
app = Server("syncline-mcp")

# Define tools
TOOLS = [
    Tool(
        name="schedule_auto",
        description=(
            "AI-powered meeting scheduling. Syncline analyzes 100+ factors including "
            "user preferences, energy patterns, timezone fairness, and meeting context "
            "to select the optimal time. Use this when you need to schedule a meeting "
            "and want AI to pick the best time."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Email addresses of meeting attendees (all must have connected calendars)",
                },
                "duration_minutes": {
                    "type": "number",
                    "description": "Meeting duration in minutes (e.g., 30, 60)",
                },
                "title": {
                    "type": "string",
                    "description": "Meeting title/subject",
                },
                "description": {
                    "type": "string",
                    "description": "Optional meeting description or agenda",
                },
                "context": {
                    "type": "string",
                    "enum": MEETING_CONTEXTS,
                    "description": f"Meeting context for AI scoring. Options: {', '.join(MEETING_CONTEXTS)}",
                },
                "earliest_date": {
                    "type": "string",
                    "description": "Optional earliest date to consider (ISO 8601 format)",
                },
                "latest_date": {
                    "type": "string",
                    "description": "Optional latest date to consider (ISO 8601 format)",
                },
                "location": {
                    "type": "string",
                    "description": "Optional meeting location",
                },
            },
            "required": ["attendees", "duration_minutes", "title", "context"],
        },
    ),
    Tool(
        name="find_availability",
        description=(
            "Find available time slots for a meeting across multiple attendees' calendars. "
            "Returns all possible slots within the specified date range."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Email addresses of meeting attendees",
                },
                "duration_minutes": {
                    "type": "number",
                    "description": "Meeting duration in minutes",
                },
                "earliest_date": {
                    "type": "string",
                    "description": "Start of search window (ISO 8601 format)",
                },
                "latest_date": {
                    "type": "string",
                    "description": "End of search window (ISO 8601 format)",
                },
            },
            "required": ["attendees", "duration_minutes", "earliest_date", "latest_date"],
        },
    ),
    Tool(
        name="get_user_calendar_status",
        description=(
            "Check if a user has connected their calendar to Syncline. "
            "Returns connection status and last sync time."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Email address of the user to check",
                },
            },
            "required": ["email"],
        },
    ),
    Tool(
        name="schedule_meeting",
        description=(
            "Schedule a meeting at a specific time slot. "
            "For AI-powered time selection, use schedule_auto instead."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Email addresses of meeting attendees",
                },
                "start_time": {
                    "type": "string",
                    "description": "Meeting start time (ISO 8601 format)",
                },
                "duration_minutes": {
                    "type": "number",
                    "description": "Meeting duration in minutes",
                },
                "title": {
                    "type": "string",
                    "description": "Meeting title/subject",
                },
                "description": {
                    "type": "string",
                    "description": "Optional meeting description or agenda",
                },
                "location": {
                    "type": "string",
                    "description": "Optional meeting location",
                },
            },
            "required": ["attendees", "start_time", "duration_minutes", "title"],
        },
    ),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution"""
    try:
        if name == "schedule_auto":
            result = await handle_schedule_auto(arguments)
        elif name == "find_availability":
            result = await handle_find_availability(arguments)
        elif name == "get_user_calendar_status":
            result = await handle_get_user_calendar_status(arguments)
        elif name == "schedule_meeting":
            result = await handle_schedule_meeting(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        import json
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Internal error",
                "message": str(e)
            }, indent=2)
        )]


# Tool handlers

async def handle_schedule_auto(args: dict) -> dict:
    """Handle schedule_auto tool"""
    # Add auto flag for agent API
    args["auto"] = True
    return await call_syncline_api("POST", "/v1/schedule/auto", args)


async def handle_find_availability(args: dict) -> dict:
    """Handle find_availability tool"""
    return await call_syncline_api("POST", "/v1/availability", args)


async def handle_get_user_calendar_status(args: dict) -> dict:
    """Handle get_user_calendar_status tool"""
    email = args["email"]
    return await call_syncline_api("GET", f"/v1/users/{quote(email)}/status", None)


async def handle_schedule_meeting(args: dict) -> dict:
    """Handle schedule_meeting tool"""
    return await call_syncline_api("POST", "/v1/schedule", args)


# HTTP helper

async def call_syncline_api(method: str, path: str, body: dict | None) -> dict:
    """Call Syncline API"""
    url = SYNCLINE_API_URL + path
    headers = {
        "Authorization": f"Bearer {SYNCLINE_API_KEY}",
    }

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        else:
            headers["Content-Type"] = "application/json"
            response = await client.request(method, url, headers=headers, json=body)

        if response.status_code >= 400:
            error_data = response.json()
            return {
                "success": False,
                "error": error_data.get("error", "Request failed"),
                "details": error_data,
            }

        data = response.json()

        # Format success response
        result = {"success": True}

        if "chosen_slot" in data:
            result.update({
                "message": "Meeting scheduled successfully with AI-selected optimal time",
                "chosen_slot": data["chosen_slot"],
                "agent_reasoning": data.get("agent_reasoning"),
                "meeting": data.get("meeting"),
            })
        elif "slots" in data:
            result.update({
                "slots": data["slots"],
                "total_slots": len(data["slots"]),
            })
        elif "meeting" in data:
            result.update({
                "message": "Meeting scheduled successfully",
                "meeting": data["meeting"],
            })
        else:
            result["user"] = data

        return result


async def main():
    """Main entry point"""
    print("Syncline MCP server running on stdio", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
