from typing import Any

import requests
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.mcp import raise_for_mcp_detail
from vector_bridge.schema.functions import FunctionLLMStructure
from vector_bridge.schema.mcp import (
    MCP,
    MCPToolExecutionRequest,
    PaginatedMCPs,
)


class MCPClient:
    """Client for MCP (Model Context Protocol) endpoints that require an API key."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def get_mcp_by_name(
        self,
        mcp_name: str,
        integration_name: str | None = None,
    ) -> MCP:
        """
        Get MCP integration by name.

        Args:
            mcp_name: The name of the MCP integration
            integration_name: The name of the Integration

        Returns:
            MCP object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/mcp"
        params = {"integration_name": integration_name, "mcp_name": mcp_name}
        headers = self.client._get_auth_headers()

        response = requests.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
        return MCP.model_validate(result)

    def get_mcp(
        self,
        mcp_id: str,
        integration_name: str | None = None,
    ) -> MCP:
        """
        Get MCP integration by ID.

        Args:
            mcp_id: The ID of the MCP integration
            integration_name: The name of the Integration

        Returns:
            MCP object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/mcp/{mcp_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        response = requests.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
        return MCP.model_validate(result)

    def list_mcps(
        self,
        limit: int = 50,
        last_evaluated_key: str | None = None,
        enabled_only: bool = False,
        integration_name: str | None = None,
    ) -> PaginatedMCPs:
        """
        List MCP integrations for an Integration.

        Args:
            limit: Maximum number of MCPs to return
            last_evaluated_key: Pagination key
            enabled_only: Only return enabled MCPs
            integration_name: The name of the Integration

        Returns:
            Paginated list of MCP integrations
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/mcps/list"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "enabled_only": enabled_only,
        }

        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()

        response = requests.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
        return PaginatedMCPs.model_validate(result)

    def run_mcp_tool(
        self,
        mcp_name: str,
        tool_request: MCPToolExecutionRequest,
        integration_name: str | None = None,
        instruction_name: str = "DEFAULT",
        agent_name: str = "DEFAULT",
    ) -> Any:
        """
        Run an MCP tool. Requires tool_name and optional arguments.

        Args:
            mcp_name: The MCP integration name to be executed
            tool_request: The MCP tool execution request
            integration_name: The name of the Integration
            instruction_name: The instruction name for messages creation or management
            agent_name: The agent name for messages creation or management

        Returns:
            Tool execution response
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/mcp/{mcp_name}/run"
        params = {
            "integration_name": integration_name,
            "instruction_name": instruction_name,
            "agent_name": agent_name,
        }
        headers = self.client._get_auth_headers()

        response = requests.post(url, headers=headers, params=params, json=tool_request.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
        return result

    def get_mcp_tools(
        self,
        mcp_name: str,
        integration_name: str | None = None,
    ) -> list[FunctionLLMStructure]:
        """
        Get available MCP tools as LLM-ready function structures.

        Args:
            mcp_name: The name of the MCP integration
            integration_name: The name of the Integration

        Returns:
            List of MCP tools as function structures
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/mcp/{mcp_name}/tools"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        response = requests.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
        return result
