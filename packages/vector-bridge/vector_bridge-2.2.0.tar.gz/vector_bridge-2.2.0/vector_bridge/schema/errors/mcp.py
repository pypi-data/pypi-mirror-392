from enum import StrEnum


class MCPError(Exception):
    """Base class for Log-related errors."""


class MCPErrorDetail(StrEnum):
    NOT_FOUND = "MCP not found"

    def to_exception(self) -> type[MCPError]:
        """Return the exception class that corresponds to this log error detail."""
        mapping = {
            MCPErrorDetail.NOT_FOUND: MCPError,
        }
        return mapping[self]


def raise_for_mcp_detail(detail: str):
    """Raise appropriate exception for MCP-related errors."""
    try:
        detail_enum = MCPErrorDetail(detail)
    except ValueError as e:
        raise MCPError(detail) from e
    raise detail_enum.to_exception()(detail)
