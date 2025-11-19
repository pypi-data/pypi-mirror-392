# VectorBridge Python SDK

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

A modern Python SDK for the [VectorBridge.ai](https://vectorbridge.ai) API with first‑class support for both synchronous and asynchronous usage. Access authentication, user/admin operations, AI processing with streaming, vector queries, workflows, and more.

## Installation

```bash
pip install vector-bridge
```

## Choose Sync or Async

- Sync client: `VectorBridgeClient`
- Async client: `AsyncVectorBridgeClient`
- Factory: `create_client(async_client: bool = False, **kwargs)`

```python
from vector_bridge import VectorBridgeClient, AsyncVectorBridgeClient, create_client
```

## Quick Start (Sync)

```python
from vector_bridge import VectorBridgeClient

# API key auth (application access)
client = VectorBridgeClient(integration_name="default", api_key="your_api_key")
print(client.ping())  # "OK"

# Or username/password (admin access)
admin = VectorBridgeClient(integration_name="default")
admin.login(username="your_email@example.com", password="your_password")
print(admin.ping())
```

## Quick Start (Async)

```python
import asyncio
from vector_bridge import AsyncVectorBridgeClient

async def main():
    async with AsyncVectorBridgeClient(integration_name="default", api_key="your_api_key") as client:
        print(await client.ping())  # "OK"

        # Or login
        # await client.login(username="your_email@example.com", password="your_password")

asyncio.run(main())
```

## Using the Factory

```python
from vector_bridge import create_client

# Sync
client = create_client(integration_name="default", api_key="your_api_key")

# Async
async_client = create_client(integration_name="default", api_key="your_api_key", async_client=True)
```

## AI Message Processing (Streaming)

### Sync
```python
from vector_bridge import VectorBridgeClient

client = VectorBridgeClient(integration_name="default", api_key="your_api_key")

stream = client.ai_message.process_message_stream(
    content="Tell me about artificial intelligence",
    chat_id="user123"
)

for chunk in stream.chunks:
    print(chunk, end="")

final_message = stream.message  # MessageInDB
```

### Async
```python
import asyncio
from vector_bridge import AsyncVectorBridgeClient

async def main():
    async with AsyncVectorBridgeClient(integration_name="default", api_key="your_api_key") as client:
        stream = await client.ai_message.process_message_stream(
            content="Tell me about artificial intelligence",
            chat_id="user123"
        )

        # stream is async-iterable
        async for chunk in stream:
            print(chunk, end="")

        final_message = await stream.message  # MessageInDB

asyncio.run(main())
```

### Structured JSON Responses

```python
from typing import List
from pydantic import BaseModel

class Crew(BaseModel):
    name: str

class MoonLandingDetails(BaseModel):
    landing_year: int
    landing_month: int
    landing_day: int
    crew: List[Crew]

# Sync
client = VectorBridgeClient(integration_name="default", api_key="your_api_key")
model = client.ai_message.process_message_model(
    content="Details about moon landing",
    response_model=MoonLandingDetails,
    chat_id="user123",
)

# Async
# async with AsyncVectorBridgeClient(...) as client:
#     model = await client.ai_message.process_message_model(
#         content="Details about moon landing",
#         response_model=MoonLandingDetails,
#         chat_id="user123",
#     )
```

### Conversation History

```python
from vector_bridge.schema.helpers.enums import SortOrder

# Sync - Vector DB
msgs = client.ai_message.fetch_messages(
    chat_id="user123", limit=50, sort_order=SortOrder.DESCENDING, near_text="machine learning"
)

# Async equivalent
# await client.ai_message.fetch_messages(...)
```

## AI Agents

```python
# Sync
chat = client.ai.set_current_agent(user_id="user123", agent_name="sales_manager")
chat = client.ai.set_core_knowledge(user_id="user123", core_knowledge={"company": "ACME", "products": ["A", "B"]})

# Async
# await client.ai.set_current_agent(user_id="user123", agent_name="sales_manager")
# await client.ai.set_core_knowledge(user_id="user123", core_knowledge={...})
```

## Running Functions

```python
# Sync
result = client.functions.run_function(
    function_name="calculator",
    a=10,
    b=5,
    operation="multiply"
)

# Async
# result = await client.functions.run_function(
#     function_name="calculator",
#     a=10,
#     b=5,
#     operation="multiply"
# )
```

## Vector Queries

```python
from weaviate.collections.classes.filters import Filter

# Sync search
search = client.queries.run_search_query(
    vector_schema="Documents",
    near_text="attention mechanism",
    limit=5,
)

# Sync find similar
# from uuid import UUID
# similar = client.queries.run_find_similar_query(
#     vector_schema="Documents",
#     near_id=UUID("8c03ff2f-36f9-45f7-9918-48766c968f45"),
#     limit=5,
# )

# Async equivalents
# await client.queries.run_search_query(...)
# await client.queries.run_find_similar_query(...)
```

## Workflows

Workflows provide multi‑step processes with status tracking, output capture, caching, and error handling. Both sync and async modes are available.

### Sync Workflow

```python
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.workflows import WorkflowCreate, WorkflowStatus
from vector_bridge.sync_io.client.workflows import Workflow, workflow_runner, cache_result


class ReportWorkflow(Workflow):
    @workflow_runner
    def run(self, user_id: str):
        data = self.fetch(user_id)
        return self.generate(data)

    @cache_result
    def fetch(self, user_id: str):
        return client.queries.run_search_query("Documents", near_text="summary", limit=3)

    @cache_result
    def generate(self, data):
        return client.functions.run_function(function_name="generate_pdf", markdown_content="...")


client = VectorBridgeClient(integration_name="default", api_key="your_api_key")
wf = ReportWorkflow(client, WorkflowCreate(workflow_id="wf_1", workflow_name="Report", status=WorkflowStatus.PENDING))
result = wf.run("user123")
```

### Async Workflow

```python
import asyncio
from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.workflows import WorkflowCreate, WorkflowStatus
from vector_bridge.async_io.client.workflows import AsyncWorkflow, async_workflow_runner, async_cache_result


class AsyncReportWorkflow(AsyncWorkflow):
    @async_workflow_runner
    async def run(self, user_id: str):
        data = await self.fetch(user_id)
        return await self.generate(data)

    @async_cache_result
    async def fetch(self, user_id: str):
        return await client.queries.run_search_query("Documents", near_text="summary", limit=3)

    @async_cache_result
    async def generate(self, data):
        return await client.functions.run_function(function_name="generate_pdf", markdown_content="...")


async def main():
    async with AsyncVectorBridgeClient(integration_name="default", api_key="your_api_key") as client:
        wf = AsyncReportWorkflow(
            client,
            WorkflowCreate(workflow_id="wf_1", workflow_name="Report", status=WorkflowStatus.PENDING)
        )
        await wf.initialize()
        result = await wf.run("user123")


asyncio.run(main())
```

## Client Highlights (Sync/Async)

Most day‑to‑day endpoints are under `client.<module>` (not `client.admin`). Typical flows: users, chats, API keys, logs, notifications, usage, AI knowledge (files/DB), queries, functions, workflows. Admin remains for organization, security groups, integrations, and function management.

Example (sync):
```python
me = client.users.get_me()
logs = client.logs.list_logs(integration_name=client.integration_name, limit=25)
```

Example (async):
```python
# me = await client.users.get_me()
# logs = await client.logs.list_logs(integration_name=client.integration_name, limit=25)
```

## AI Knowledge: File Storage (Sync and Async)

### Sync file workflow
```python
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.ai_knowledge.filesystem import AIKnowledgeFileSystemFilters, AIKnowledgeFileSystemItemUpdate
from vector_bridge.schema.helpers.enums import FileAccessType

client = VectorBridgeClient(integration_name="default", api_key="your_api_key")

# Create folder
folder = client.ai_knowledge.file_storage.create_folder(
    folder_name="Project Documents",
    folder_description="Docs for Q4",
    private=True,
)

# Upload a file with vectorization and progress
upload = client.ai_knowledge.file_storage.upload_file(
    file_path="./docs/spec.pdf",
    parent_id=folder.uuid,
    vectorized=True,
    tags=["spec", "q4"],
)

for p in upload.progress_updates:
    print("progress:", p)
item = upload.item

# Update metadata
client.ai_knowledge.file_storage.update_file_or_folder(
    item_id=item.uuid,
    updated_properties=AIKnowledgeFileSystemItemUpdate(starred=True, tags=["spec", "approved"]) 
)

# Share read-only with a user
client.ai_knowledge.file_storage.grant_or_revoke_user_access(
    item_id=item.uuid, user_id="user-123", has_access=True, access_type=FileAccessType.READ
)

# List items under folder
items = client.ai_knowledge.file_storage.list_files_and_folders(
    filters=AIKnowledgeFileSystemFilters(parent_id=folder.uuid)
)

# Download link
link = client.ai_knowledge.file_storage.get_download_link_for_document(item_id=item.uuid)
```

### Async file workflow
```python
import asyncio
from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.ai_knowledge.filesystem import AIKnowledgeFileSystemFilters, AIKnowledgeFileSystemItemUpdate
from vector_bridge.schema.helpers.enums import FileAccessType

async def main():
    async with AsyncVectorBridgeClient(integration_name="default", api_key="your_api_key") as client:
        folder = await client.ai_knowledge.file_storage.create_folder(
            folder_name="Research",
            folder_description="ML papers",
            private=False,
        )

        upload = await client.ai_knowledge.file_storage.upload_file(
            file_path="./papers/attention.pdf",
            parent_id=folder.uuid,
            vectorized=True,
            tags=["nlp", "transformers"],
        )

        async for p in upload.progress_updates:
            print("progress:", p)
        item = await upload.item

        await client.ai_knowledge.file_storage.update_file_or_folder(
            item_id=item.uuid,
            updated_properties=AIKnowledgeFileSystemItemUpdate(starred=True)
        )

        await client.ai_knowledge.file_storage.grant_or_revoke_user_access(
            item_id=item.uuid, user_id="user-123", has_access=True, access_type=FileAccessType.READ
        )

        items = await client.ai_knowledge.file_storage.list_files_and_folders(
            filters=AIKnowledgeFileSystemFilters(parent_id=folder.uuid)
        )

        link = await client.ai_knowledge.file_storage.get_download_link_for_document(item_id=item.uuid)

asyncio.run(main())
```

## Function Management (Create via Admin, Run via Client)

```python
from vector_bridge.schema.functions import CodeExecuteFunctionCreate, FunctionParametersStorageStructure,
    FunctionPropertyStorageStructure
from vector_bridge.schema.helpers.enums import AIActions

# Create a CODE_EXEC function (sync)
fn = client.admin.functions.add_function(
    function_data=CodeExecuteFunctionCreate(
        function_name="calculator",
        description="Perform math operations",
        function_parameters=FunctionParametersStorageStructure(
            properties=[
                FunctionPropertyStorageStructure(name="a", description="First operand"),
                FunctionPropertyStorageStructure(name="b", description="Second operand"),
                FunctionPropertyStorageStructure(name="operation", description="add|sub|mul|div"),
            ]
        ),
        code="""
def run(**kwargs):
    a = float(kwargs.get('a'))
    b = float(kwargs.get('b'))
    op = kwargs.get('operation')
    if op == 'add': return a + b
    if op == 'sub': return a - b
    if op == 'mul': return a * b
    if op == 'div': return a / b
    return None
""",
        function_action=AIActions.CODE_EXEC,
    )
)


# Register a native Python function quickly
def monthly_payment(principal: float, annual_rate: float, years: float) -> float:
    """Calculate monthly loan payment.

    Args:
        principal: Loan amount in dollars
        annual_rate: Annual interest rate in percent
        years: Loan term in years
    """
    m = annual_rate / 100 / 12
    n = years * 12
    return round(principal * (m * (1 + m) ** n) / ((1 + m) ** n - 1), 2)


client.admin.functions.add_python_function(monthly_payment)

# Execute via functions client (sync)
res = client.functions.run_function(function_name="calculator", a=2, b=8, operation="mul")

# Async
# res = await client.functions.run_function(function_name="calculator", a=2, b=8, operation="mul")
```

## Error Handling

Errors are raised as domain‑specific exceptions. For generic HTTP errors you may see `HTTPException` with `status_code` and `detail`.

```python
from vector_bridge import VectorBridgeClient
from vector_bridge.schema.error import HTTPException

client = VectorBridgeClient(integration_name="default")
try:
    client.login(username="user@example.com", password="wrong_password")
except HTTPException as e:
    print(f"HTTP {e.status_code}: {e.detail}")
```

## License

MIT License. See `LICENSE` for details.