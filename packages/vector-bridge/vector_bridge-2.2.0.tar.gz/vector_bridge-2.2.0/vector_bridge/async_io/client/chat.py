from typing import Any

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.chat import Chat, ChatsList
from vector_bridge.schema.errors.chat import raise_for_chat_detail
from vector_bridge.schema.errors.message import raise_for_message_detail
from vector_bridge.schema.helpers.enums import SortOrder
from vector_bridge.schema.messages import MessagesList


class AsyncChatClient:
    """Async client for chat management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def fetch_messages(
        self,
        chat_id: str,
        integration_name: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = SortOrder.DESCENDING,
        near_text: str | None = None,
    ) -> MessagesList:
        """
        Retrieve messages from vector database.

        Args:
            chat_id: User ID
            integration_name: The name of the integration
            limit: Number of messages to return
            offset: Starting point for fetching records
            sort_order: Order to sort results (asc/desc)
            near_text: Text to search for semantically similar messages

        Returns:
            MessagesList with messages and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/chat/messages"
        params = {
            "user_id": chat_id,
            "integration_name": integration_name,
            "limit": limit,
            "offset": offset,
            "sort_order": sort_order.value,
        }
        if near_text:
            params["near_text"] = near_text

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_message_detail)
            return MessagesList.model_validate(result)

    async def set_current_agent(
        self,
        user_id: str,
        agent_name: str,
        integration_name: str | None = None,
        instruction_name: str = "default",
    ) -> Chat:
        """
        Set the current agent.

        Args:
            user_id: User ID
            agent_name: The agent to set
            integration_name: The name of the Integration
            instruction_name: The name of the instruction

        Returns:
            Chat object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/chat/set/agent"
        params = {
            "user_id": user_id,
            "integration_name": integration_name,
            "instruction_name": instruction_name,
            "agent_name": agent_name,
        }

        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return Chat.model_validate(result)

    async def set_core_knowledge(
        self, user_id: str, core_knowledge: dict[str, Any], integration_name: str | None = None
    ) -> Chat:
        """
        Set the core knowledge.

        Args:
            user_id: User ID
            core_knowledge: The core knowledge to set
            integration_name: The name of the Integration

        Returns:
            Chat object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/chat/set/core-knowledge"
        params = {"user_id": user_id, "integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params, json=core_knowledge) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return Chat.model_validate(result)

    async def fetch_chats_for_my_organization(
        self, integration_name: str | None = None, limit: int = 50, offset: int = 0
    ) -> ChatsList:
        """
        Retrieve a list of chat sessions associated with the organization.

        Args:
            integration_name: The name of the integration
            limit: Number of chat records to return
            offset: Starting point for fetching records

        Returns:
            ChatsList with chats and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/chats"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "offset": offset,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return ChatsList.model_validate(result)

    async def fetch_my_chats(self, integration_name: str | None = None, limit: int = 50, offset: int = 0) -> ChatsList:
        """
        Retrieve a list of chat sessions for the current user.

        Args:
            integration_name: The name of the integration
            limit: Number of chat records to return
            offset: Starting point for fetching records

        Returns:
            ChatsList with chats and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/chats/me"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "offset": offset,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return ChatsList.model_validate(result)

    async def get_chat(self, chat_id: str, integration_name: str | None = None) -> ChatsList:
        """
        Retrieve a list of chat sessions for the current user.

        Args:
            chat_id: Chat ID
            integration_name: The name of the integration

        Returns:
            ChatsList with chats and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/chats/me"
        params = {
            "chat_id": chat_id,
            "integration_name": integration_name,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return ChatsList.model_validate(result)

    async def delete_chat(self, chat_id: str, integration_name: str | None = None) -> None:
        """
        Delete a chat session between the organization and a specific user.

        Args:
            chat_id: The unique identifier of the user
            integration_name: The name of the integration
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/chat/delete/{chat_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            if response.status != 204:
                await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)

    async def create_chat(self, chat_id: str, title: str = "New Chat", integration_name: str | None = None) -> Chat:
        """
        Create a new chat session between the organization and a specific user.

        Args:
            chat_id: Unique identifier of the user
            title: Title for the new chat
            integration_name: Name of the integration

        Returns:
            Chat: The newly created chat session
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/chat/create/{chat_id}"
        params = {
            "integration_name": integration_name,
            "title": title,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_chat_detail)
            return Chat.model_validate(result)
