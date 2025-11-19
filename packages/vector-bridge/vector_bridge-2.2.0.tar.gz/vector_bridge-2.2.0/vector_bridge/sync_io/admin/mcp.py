import json
import os

import requests
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.mcp import raise_for_mcp_detail
from vector_bridge.schema.mcp import (
    MCP,
    MCPCreate,
    MCPUpdate,
)


class MCPAdmin:
    """Admin client for MCP (Model Context Protocol) management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def create_mcp(
        self,
        mcp_create: MCPCreate,
        zip_file_path: str,
        integration_name: str | None = None,
    ) -> MCP:
        """
        Create new MCP (Model Context Protocol) integration.

        Args:
            mcp_create: MCP creation data
            zip_file_path: Path to the MCP ZIP file
            integration_name: The name of the Integration

        Returns:
            Created MCP object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/mcp/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        # Prepare form data
        data = {
            "name": mcp_create.mcp_name,
            "description": mcp_create.description,
            "allow_patterns": json.dumps(mcp_create.allow_patterns),
            "deny_patterns": json.dumps(mcp_create.deny_patterns),
        }

        # Extract filename from path and prepare file data
        zip_filename = os.path.basename(zip_file_path)

        with open(zip_file_path, "rb") as zip_file:
            files = {"zip_file": (zip_filename, zip_file, "application/zip")}
            response = requests.post(url, headers=headers, params=params, data=data, files=files)
        result = self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
        return MCP.model_validate(result)

    def update_mcp(
        self,
        mcp_id: str,
        mcp_update: MCPUpdate,
        integration_name: str | None = None,
    ) -> MCP:
        """
        Update an existing MCP integration.

        Args:
            mcp_id: The ID of the MCP integration
            mcp_update: Updated MCP data
            integration_name: The name of the Integration

        Returns:
            Updated MCP object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/mcp/{mcp_id}/update"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        response = requests.put(
            url,
            headers=headers,
            params=params,
            json=mcp_update.model_dump(exclude_none=True),
        )
        result = self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
        return MCP.model_validate(result)

    def delete_mcp(
        self,
        mcp_id: str,
        integration_name: str | None = None,
    ) -> None:
        """
        Delete MCP integration.

        Args:
            mcp_id: The MCP integration ID
            integration_name: The name of the Integration
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/mcp/{mcp_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        response = requests.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
