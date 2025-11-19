from datetime import datetime

from pydantic import BaseModel, Field


class MCP(BaseModel):
    """MCP (Model Context Protocol) integration model."""

    model_config = {"from_attributes": True}

    mcp_id: str
    integration_id: str
    mcp_name: str = Field(..., description="Name of the MCP integration")
    zip_filename: str = Field(..., description="Original filename of the MCP .zip file")
    zip_content_hash: str = Field(..., description="Hash of the ZIP file content for integrity")
    allow_patterns: list[str] = Field(
        default_factory=list,
        description="List of allowed tool patterns (e.g., 'get*', 'list*', 'get_secret_tool')",
    )
    deny_patterns: list[str] = Field(
        default_factory=list,
        description="List of denied tool patterns (e.g., 'delete*', 'admin*')",
    )
    description: str = Field(default="", description="Description of the MCP integration")
    enabled: bool = Field(default=True, description="Whether the MCP integration is enabled")
    created_at: datetime | None = Field(default=None)
    created_by: str | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    updated_by: str | None = Field(default=None)


class MCPCreate(BaseModel):
    """Schema for creating MCP (Model Context Protocol) integrations."""

    mcp_name: str = Field(..., description="Name of the MCP integration")
    allow_patterns: list[str] = Field(
        default_factory=list,
        description="List of allowed tool patterns (e.g., 'get*', 'list*', 'get_secret_tool')",
    )
    deny_patterns: list[str] = Field(
        default_factory=list,
        description="List of denied tool patterns (e.g., 'delete*', 'admin*')",
    )
    description: str = Field(default="", description="Description of the MCP integration")


class MCPUpdate(BaseModel):
    """Schema for updating MCP integrations."""

    mcp_name: str | None = Field(default=None, description="Updated name of the MCP integration")
    allow_patterns: list[str] | None = Field(default=None, description="Updated list of allowed tool patterns")
    deny_patterns: list[str] | None = Field(default=None, description="Updated list of denied tool patterns")
    description: str | None = Field(default=None, description="Updated description")
    enabled: bool | None = Field(default=None, description="Updated enabled status")


class PaginatedMCPs(BaseModel):
    """Paginated list of MCP integrations."""

    mcps: list[MCP] = Field(default_factory=list)
    limit: int
    last_evaluated_key: str | None = None
    has_more: bool = False


class MCPToolExecutionRequest(BaseModel):
    """Request to execute an MCP tool."""

    tool_name: str = Field(..., description="The name of the MCP tool to execute")
    arguments: dict = Field(default_factory=dict, description="Arguments to pass to the MCP tool")


class MCPToolExecutionResponse(BaseModel):
    """Response from MCP tool execution."""

    success: bool
    result: dict | str | None = None
    error: str | None = None
    execution_time_ms: int | None = None
