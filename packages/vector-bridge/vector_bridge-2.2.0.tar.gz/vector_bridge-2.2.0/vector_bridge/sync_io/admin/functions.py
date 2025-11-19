from collections.abc import Callable

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.errors.functions import raise_for_function_detail
from vector_bridge.schema.functions import (
    CodeExecuteFunctionCreate,
    CodeExecuteFunctionUpdate,
    Function,
    FunctionExtractor,
    JsonFunctionCreate,
    JsonFunctionUpdate,
    SemanticSearchFunctionCreate,
    SemanticSearchFunctionUpdate,
    SimilarSearchFunctionCreate,
    SimilarSearchFunctionUpdate,
    SummaryFunctionCreate,
    SummaryFunctionUpdate,
)


class FunctionsAdmin:
    """Admin client for functions management endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def add_function(
        self,
        function_data: (
            SemanticSearchFunctionCreate
            | SimilarSearchFunctionCreate
            | SummaryFunctionCreate
            | JsonFunctionCreate
            | CodeExecuteFunctionCreate
        ),
        integration_name: str | None = None,
    ) -> Function:
        """
        Add new Function to the integration.

        Args:
            function_data: Function details
            integration_name: The name of the Integration

        Returns:
            Created function object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/function/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=function_data.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_function_detail)
        return Function.to_valid_subclass(result)

    def add_python_function(
        self,
        function: Callable,
        integration_name: str | None = None,
    ) -> Function:
        """
        Add a Python function directly.

        This automatically extracts the function's code, signature, and documentation
        to create a CODE_EXEC function that can be called remotely.

        Args:
            function: The Python function to add (must have type annotations and docstrings)
            integration_name: The name of the Integration

        Returns:
            Created function object
        """
        # Extract function metadata and code
        extractor = FunctionExtractor(function)
        function_data = extractor.get_function_metadata()

        # Create the CodeExecuteFunctionCreate model
        function_model = CodeExecuteFunctionCreate.model_validate(function_data)

        # Call the existing add_function method
        return self.add_function(function_model, integration_name)

    def update_function(
        self,
        function_id: str,
        function_data: (
            SemanticSearchFunctionUpdate
            | SimilarSearchFunctionUpdate
            | SummaryFunctionUpdate
            | JsonFunctionUpdate
            | CodeExecuteFunctionUpdate
        ),
        integration_name: str | None = None,
    ) -> Function:
        """
        Update an existing Function.

        Args:
            function_id: The ID of the Function to update
            function_data: Updated function details
            integration_name: The name of the Integration

        Returns:
            Updated function object
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/function/{function_id}/update"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.put(url, headers=headers, params=params, json=function_data.model_dump())
        result = self.client._handle_response(response=response, error_callable=raise_for_function_detail)
        return Function.to_valid_subclass(result)

    def delete_function(self, function_id: str, integration_name: str | None = None) -> None:
        """
        Delete a function.

        Args:
            function_id: The ID of the function to delete
            integration_name: The name of the Integration
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/function/{function_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()
        response = self.client.session.delete(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_function_detail)
