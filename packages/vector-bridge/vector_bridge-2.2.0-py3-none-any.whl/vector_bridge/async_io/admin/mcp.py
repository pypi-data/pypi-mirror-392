import json
import os

from aiohttp import FormData
from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.mcp import raise_for_mcp_detail
from vector_bridge.schema.mcp import (
    MCP,
    MCPCreate,
    MCPUpdate,
)


class AsyncMCPAdmin:
    """Async admin client for MCP (Model Context Protocol) management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def create_mcp(
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
        await self.client._ensure_session()

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

        # Extract filename from path
        zip_filename = os.path.basename(zip_file_path)

        # For aiohttp, we need to use FormData
        form_data = FormData()
        for key, value in data.items():
            form_data.add_field(key, value)

        # Read and add the file
        with open(zip_file_path, "rb") as zip_file:
            form_data.add_field(
                "zip_file",
                zip_file,
                filename=zip_filename,
                content_type="application/zip",
            )

        async with self.client.session.post(url, headers=headers, params=params, data=form_data) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
            return MCP.model_validate(result)

    async def update_mcp(
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
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/mcp/{mcp_id}/update"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.put(
            url,
            headers=headers,
            params=params,
            json=mcp_update.model_dump(exclude_none=True),
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
            return MCP.model_validate(result)

    async def delete_mcp(
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
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/mcp/{mcp_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_mcp_detail)
