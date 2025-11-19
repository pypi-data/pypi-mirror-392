#!/usr/bin/env python3
"""
🤖 Architect Agent Script for Ontologia

Runs an AI architect agent via MCP server for automated ontology operations.
Uses Pydantic AI to select and execute MCP tools with structured responses.

Usage:
    python scripts/run_architect_agent.py [options] [prompt]

Examples:
    python scripts/run_architect_agent.py "Create ObjectType 'product' with sku and name"
    python scripts/run_architect_agent.py --model gpt-4o "Create complex ontology"
    python scripts/run_architect_agent.py --dry-run --list-tools

Environment Variables:
    OPENAI_API_KEY - OpenAI API key (required)
    ONTOLOGIA_AGENT_TOKEN - Service account token (required)
    ONTOLOGIA_MCP_URL - MCP server URL (auto-detected if not set)
    ONTOLOGIA_AGENT_MODEL - LLM model name (default: openai:gpt-4o-mini)

Features:
    - Structured AI agent responses
    - Tool catalog discovery
    - Model selection and configuration
    - Dry-run mode for testing
    - Comprehensive error handling
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from rich.console import Console

from scripts.utils import BaseCLI, ExitCode, optional_import

# Lazy imports for optional dependencies
fastmcp = optional_import("fastmcp", install_group="agents")
pydantic_ai = optional_import("pydantic-ai", install_group="agents")

from ontologia.config import load_config


class ActionPlan(BaseModel):
    """Structured response produced by the Architect agent."""

    tool_name: str
    arguments: dict[str, Any]
    justification: str


class ArchitectAgentCLI(BaseCLI):
    """CLI for the Architect agent operations."""

    def __init__(self) -> None:
        super().__init__(
            name="run_architect_agent",
            description="Run AI architect agent via MCP server for automated ontology operations",
            version="1.0.0",
        )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "prompt",
            nargs="?",
            default="Crie um ObjectType 'product' com primary key 'sku' e propriedades obrigatórias 'sku' e 'name'.",
            help="Instruction for the agent",
        )
        parser.add_argument(
            "--model",
            help="Override LLM model name (e.g., openai:gpt-4o, openai:gpt-4o-mini)",
        )
        parser.add_argument(
            "--api-url",
            help="Ontologia API base URL (auto-detected if not provided)",
        )
        parser.add_argument(
            "--mcp-url",
            help="MCP server URL (auto-detected if not provided)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be executed without running the agent",
        )
        parser.add_argument(
            "--list-tools",
            action="store_true",
            help="List available MCP tools and exit",
        )
        parser.add_argument(
            "--validate-config",
            action="store_true",
            help="Validate configuration and exit",
        )

    def run(self, args) -> ExitCode:
        # Validate dependencies first
        try:
            fastmcp()
            pydantic_ai()
        except Exception as e:
            self.console.print(f"❌ Failed to import agent dependencies: {e}")
            self.console.print("Install with: uv sync --group agents")
            return ExitCode.MISSING_DEPENDENCIES

        if args.validate_config:
            return self._validate_config(args)

        if args.list_tools:
            return self._list_tools(args)

        if args.dry_run:
            return self._dry_run(args)

        return self._run_agent(args)

    def _validate_config(self, args) -> ExitCode:
        """Validate configuration and environment."""
        self.console.print("🔍 Validating agent configuration...")

        # Check required environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.console.print("❌ OPENAI_API_KEY must be set")
            return ExitCode.CONFIGURATION_ERROR

        token = os.getenv("ONTOLOGIA_AGENT_TOKEN")
        if not token:
            self.console.print("❌ ONTOLOGIA_AGENT_TOKEN must be set")
            return ExitCode.CONFIGURATION_ERROR

        # Check configuration
        try:
            config = self._get_config(args)
            self.console.print(f"✅ API URL: {config['api_url']}")
            self.console.print(f"✅ MCP URL: {config['mcp_url']}")
            self.console.print(f"✅ Model: {config['model_name']}")
        except Exception as e:
            self.console.print(f"❌ Configuration error: {e}")
            return ExitCode.CONFIGURATION_ERROR

        self.console.print("✅ Configuration validation passed")
        return ExitCode.SUCCESS

    def _list_tools(self, args) -> ExitCode:
        """List available MCP tools."""
        try:
            config = self._get_config(args)
            tools = asyncio.run(self._gather_tools(config["mcp_url"], config["token"]))

            self.console.print("🛠️  Available MCP Tools:")
            for tool in tools:
                schema = json.dumps(tool["schema"], indent=2, sort_keys=True)
                description = tool.get("description", "No description provided.")
                self.console.print(f"\n- {tool['name']}: {description}")
                self.console.print(f"  Schema: {schema}")

            return ExitCode.SUCCESS

        except Exception as e:
            self.console.print(f"❌ Failed to list tools: {e}")
            return ExitCode.GENERAL_ERROR

    def _dry_run(self, args) -> ExitCode:
        """Show what would be executed without running the agent."""
        self.console.print("🔍 Dry run mode - agent execution plan:")

        config = self._get_config(args)

        self.console.print("\n⚙️  Configuration:")
        self.console.print(f"  API URL: {config['api_url']}")
        self.console.print(f"  MCP URL: {config['mcp_url']}")
        self.console.print(f"  Model: {config['model_name']}")

        self.console.print("\n📝 Prompt:")
        self.console.print(f"  {args.prompt}")

        self.console.print("\n🔄 Execution Steps:")
        self.console.print("  1. Connect to MCP server")
        self.console.print("  2. Gather available tools")
        self.console.print("  3. Initialize AI agent with tool catalog")
        self.console.print("  4. Process prompt and generate action plan")
        self.console.print("  5. Execute selected tool")
        self.console.print("  6. Return results")

        return ExitCode.SUCCESS

    def _run_agent(self, args) -> ExitCode:
        """Execute the architect agent."""
        try:
            result = asyncio.run(run_architect_agent(args.prompt, self._get_config(args)))
            return ExitCode.SUCCESS if result else ExitCode.GENERAL_ERROR
        except Exception as e:
            self.console.print(f"❌ Agent execution failed: {e}")
            self.logger.exception("Agent execution failed")
            return ExitCode.GENERAL_ERROR

    def _get_config(self, args) -> dict[str, Any]:
        """Get configuration from arguments and environment."""
        # Load base configuration
        ontologia_config = load_config(Path(os.getenv("ONTOLOGIA_CONFIG_ROOT", Path.cwd())))

        # Determine URLs
        api_url = args.api_url or os.getenv("ONTOLOGIA_API_URL", ontologia_config.api.base_url)
        mcp_url = args.mcp_url or os.getenv("ONTOLOGIA_MCP_URL", f"{api_url.rstrip('/')}/mcp")

        # Get model name
        model_name = args.model or os.getenv("ONTOLOGIA_AGENT_MODEL", "openai:gpt-4o-mini")

        # Get token
        token = os.getenv("ONTOLOGIA_AGENT_TOKEN")
        if not token:
            raise ValueError("ONTOLOGIA_AGENT_TOKEN must be set")

        return {
            "api_url": api_url,
            "mcp_url": mcp_url,
            "model_name": model_name,
            "token": token,
            "api_key": os.getenv("OPENAI_API_KEY"),
        }

    async def _gather_tools(self, mcp_url: str, token: str) -> list[dict[str, Any]]:
        """Gather available tools from MCP server."""
        fastmcp_client = fastmcp()

        auth_header = f"Bearer {token}"
        async with fastmcp_client.Client(mcp_url, auth=auth_header) as client:
            tools = await client.list_tools()

            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "schema": tool.inputSchema,
                }
                for tool in tools
            ]


async def run_architect_agent(prompt: str, config: dict[str, Any]) -> bool:
    """Run the architect agent with the given prompt and configuration."""
    # Import required modules
    fastmcp_client = fastmcp()
    agent_module = pydantic_ai()

    # Validate required configuration
    api_key = config.get("api_key")
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set to run the architect agent.")

    token = config.get("token")
    if not token:
        raise ValueError("ONTOLOGIA_AGENT_TOKEN must be set with a service account token.")

    # Connect to MCP server
    auth_header = f"Bearer {token}"
    async with fastmcp_client.Client(config["mcp_url"], auth=auth_header) as client:
        catalog_text = await _gather_tools(client)

        # Build system prompt
        system_prompt = (
            "You are the Ontologia Architect agent. "
            "Select exactly one MCP tool to fulfill the user request. "
            "Respond with JSON matching the ActionPlan schema.\n\n"
            "Available tools:\n"
            f"{catalog_text}\n\n"
            "Rules:\n"
            "- tool_name must be one of the listed tools.\n"
            "- arguments must conform to the tool's JSON schema.\n"
            "- justification should briefly explain why the tool was chosen."
        )

        # Initialize agent
        agent = agent_module.Agent(
            config["model_name"],
            output_type=ActionPlan,
            system_prompt=system_prompt,
            defer_model_check=True,
        )

        console = Console()
        console.print("🤖 Agent thinking…\n")

        # Run agent
        plan_result = await agent.run(prompt)
        plan = plan_result.output

        console.print("🛠️  Selected tool:", plan.tool_name)
        console.print("📋 Arguments:\n", json.dumps(plan.arguments, indent=2))

        # Execute tool
        call_result = await client.call_tool(plan.tool_name, plan.arguments)
        if call_result.is_error:
            console.print("❌ Tool call failed. See MCP logs for details.")
            return False

        # Display results
        outcome = (
            call_result.data
            or call_result.structured_content
            or [getattr(block, "text", None) for block in call_result.content]
        )
        console.print(
            "✅ Tool call succeeded. Outcome:\n", json.dumps(outcome, indent=2, default=str)
        )

        return True


async def _gather_tools(client) -> str:
    """Gather tools and format as catalog text."""
    tools = await client.list_tools()
    lines: list[str] = []
    for tool in tools:
        schema = json.dumps(tool.inputSchema, indent=2, sort_keys=True)
        description = tool.description or "No description provided."
        lines.append(f"- {tool.name}: {description}\n  schema: {schema}")
    return "\n".join(lines)


def main() -> ExitCode:
    """Main entry point for the architect agent script."""
    cli = ArchitectAgentCLI()
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
