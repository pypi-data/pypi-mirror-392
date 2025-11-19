import json
from typing import Any

from pydantic import BaseModel
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.functions import raise_for_function_detail
from vector_bridge.schema.functions import Function, PaginatedFunctions


class FunctionClient:
    """User client for function endpoints that require an API key."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def get_function_by_name(self, function_name: str, integration_name: str | None = None) -> Function | None:
        """
        Get the Function by name.

        Args:
            function_name: The name of the Function
            integration_name: The name of the Integration

        Returns:
            Function object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/function"
        params = {"integration_name": integration_name, "function_name": function_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        if response.status_code == 404:
            return None

        result = self.client._handle_response(response=response, error_callable=raise_for_function_detail)
        return Function.to_valid_subclass(result)

    def get_function_by_id(self, function_id: str, integration_name: str | None = None) -> Function | None:
        """
        Get the Function by ID.

        Args:
            function_id: The ID of the Function
            integration_name: The name of the Integration

        Returns:
            Function object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/function/{function_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        if response.status_code == 404:
            return None

        result = self.client._handle_response(response=response, error_callable=raise_for_function_detail)
        return Function.to_valid_subclass(result)

    def list_functions(
        self,
        integration_name: str | None = None,
        limit: int = 10,
        last_evaluated_key: str | None = None,
        sort_by: str = "created_at",
    ) -> PaginatedFunctions:
        """
        List Functions for an Integration.

        Args:
            integration_name: The name of the Integration
            limit: Number of functions to retrieve
            last_evaluated_key: Pagination key for the next set of results
            sort_by: Field to sort by (created_at or updated_at)

        Returns:
            Dict with functions and pagination info
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/functions/list"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "sort_by": sort_by,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_function_detail)
        return PaginatedFunctions.resolve_functions(result)

    def list_default_functions(
        self,
    ) -> PaginatedFunctions:
        """
        List Functions for an Integration.

        Args:
            integration_name: The name of the Integration
            limit: Number of functions to retrieve
            last_evaluated_key: Pagination key for the next set of results
            sort_by: Field to sort by (created_at or updated_at)

        Returns:
            Dict with functions and pagination info
        """
        url = f"{self.client.base_url}/v1/functions/list-default"

        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers)
        result = self.client._handle_response(response=response, error_callable=raise_for_function_detail)
        return PaginatedFunctions.resolve_functions(result)

    def run_function(
        self,
        function_name: str,
        integration_name: str | None = None,
        instruction_name: str = "default",
        agent_name: str = "default",
        **kwargs,
    ) -> Any:
        """
        Run a function.

        Args:
            function_name: The name of the function to run
            integration_name: The name of the Integration
            instruction_name: The name of the instruction
            agent_name: The name of the agent

        Returns:
            Function execution result
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        response_format = kwargs.get("response_format")
        if isinstance(response_format, type) and issubclass(response_format, BaseModel):
            kwargs["response_format"] = response_format.model_json_schema()

        url = f"{self.client.base_url}/v1/function/{function_name}/run"
        params = {
            "integration_name": integration_name,
            "instruction_name": instruction_name,
            "agent_name": agent_name,
        }

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=kwargs, stream=True)
        if response.status_code >= 400:
            self.client._handle_response(response=response, error_callable=raise_for_function_detail)

        text = response.text
        try:
            return json.loads(text)
        except json.decoder.JSONDecodeError:
            return text
