"""
Integration layer for the Model Context Protocol server implementation.

This module provides the main integration point between SWE-agent's existing
ACI features and the MCP server interface, maintaining all optimizations
while providing a standardized protocol interface.
"""

from typing import Dict, List, Optional
from pathlib import Path

from sweagent.tools.commands import Command, get_available_commands
from .server import MCPServer, MCPTool
from .features import ACIFeatures
from .resources import FileResource
from .tools import command_to_mcp_tool


class ACIMCPServer(MCPServer):
    """
    MCP server implementation that integrates SWE-agent's ACI features.

    This class provides the main integration point between SWE-agent's
    existing command system and optimizations and the MCP protocol interface.
    It maintains all existing optimizations while providing a standardized
    way for agents to interact with the system.
    """

    def __init__(self):
        """Initialize the ACI MCP server with all features enabled."""
        super().__init__()
        self.features = ACIFeatures()
        self.load_commands()

    def load_commands(self) -> None:
        """
        Load all available SWE-agent commands as MCP tools.

        This method converts all existing SWE-agent commands to MCP tools
        while preserving their functionality and metadata.
        """
        for command in get_available_commands():
            tool = command_to_mcp_tool(command)
            self.register_tool(tool)

    def execute_tool(self, name: str, parameters: Dict) -> Dict:
        """
        Execute an MCP tool with the given parameters.

        Args:
            name: Name of the tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution results

        Raises:
            ValueError: If tool doesn't exist or parameters are invalid
        """
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")

        # Find the original command
        commands = get_available_commands()
        command = next((cmd for cmd in commands if cmd.name == name), None)
        if command is None:
            raise ValueError(f"Command not found for tool: {name}")

        # Execute with proper parameter validation
        return command.execute(**parameters)

    def register_file(self, path: str) -> FileResource:
        """
        Register a file as an MCP resource.

        Args:
            path: Path to the file

        Returns:
            The registered FileResource

        Raises:
            ValueError: If path is invalid
        """
        resource = FileResource(path)
        self.register_resource(resource)
        return resource

    def lint_code(self, code: str) -> List[str]:
        """
        Perform syntactic linting using ACI features.

        Args:
            code: Code to lint

        Returns:
            List of linting errors/warnings
        """
        return self.features.lint_code(code)

    def view_file(self, uri: str, start: int = 0, end: Optional[int] = None) -> str:
        """
        View file contents using ACI optimizations.

        Args:
            uri: Resource URI (file:// scheme)
            start: Starting line number
            end: Ending line number

        Returns:
            File contents

        Raises:
            ValueError: If URI is invalid or resource not found
        """
        if not uri.startswith("file://"):
            raise ValueError("Only file:// URIs are supported")

        path = uri[7:]  # Remove file:// prefix
        return self.features.view_file(path, start, end)

    def search_directory(self, pattern: str, path: str = '.') -> List[str]:
        """
        Perform directory search using ACI optimizations.

        Args:
            pattern: Search pattern
            path: Directory to search in

        Returns:
            List of matching paths
        """
        return self.features.search_directory(pattern, path)
