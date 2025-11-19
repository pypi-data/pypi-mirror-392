# Cortex AI Python SDK - [usecortex.ai](https://www.usecortex.ai/)

The official Python SDK for the Cortex AI platform. Build powerful, context-aware AI applications in your Python applications.

**Cortex** is your plug-and-play memory infrastructure. It powers intelligent, context-aware retrieval for any AI app or agent. Whether you’re building a customer support bot, research copilot, or internal knowledge assistant.

[Learn more about the SDK from our docs](https://docs.usecortex.ai/)

## Core features

* **Dynamic retrieval and querying** that always retrieve the most relevant context
* **Built-in long-term memory** that evolves with every user interaction
* **Personalization hooks** for user preferences, intent, and history
* **Developer-first SDK** with the most flexible APIs and fine-grained controls

## Getting started

### Installation

```bash
pip install usecortex-ai
```

### Client setup

We provide both synchronous and asynchronous clients. Use **`AsyncCortexAI`** when working with async/await patterns, and **`CortexAI`** for traditional synchronous workflows. Client initialization does not trigger any network requests, so you can safely create as many client instances as needed. Both clients expose the exact same set of methods.

```python
import os
from usecortex_ai import CortexAI, AsyncCortexAI

api_key = os.environ["CORTEX_API_KEY"]  # Set your Cortex API key in the environment variable CORTEX_API_KEY. Optional, but recommended.

# Sync client
client = CortexAI(token=api_key)

# Async client (for async/await usage)
async_client = AsyncCortexAI(token=api_key)
```

### Create a Tenant

You can consider a `tenant` as a single database that can have internal isolated collections called `sub-tenants`. [Know more about the concept of tenant here](https://docs.usecortex.ai/essentials/multi-tenant)

```python
def create_tenant():
    return client.user.create_tenant(tenant_id="my-company")
```

### Index Your Data

When you index your data, you make it ready for retrieval from Cortex using natural language.

```python
# Upload text content
def upload_text():
    return client.upload.upload_text(
        tenant_id="my-company-py-sync",
        sub_tenant_id="engineering",
        content="Our API rate limits are 1000 requests per minute for premium accounts.",
        file_id="api-docs-rate-limits",
        tenant_metadata={"sub_tenant_id": "engineering"}
    )

# Upload document file
def upload_file():
    with open("company-handbook.pdf", 'rb') as file_obj:
        file_data = ("company-handbook.pdf", file_obj)
        return client.upload.upload_document(
            tenant_id="my-company",
            file=file_data,
            file_id="company-handbook.pdf"
        )
```

**For a more detailed explanation** of document upload, including supported file formats, processing pipeline, metadata handling, and advanced configuration options, refer to the [Upload Document endpoint documentation](https://docs.usecortex.ai/api-reference/endpoint/upload-document).

### Search and retrieval

```python
# Semantic search with retrieval
results = client.search.retrieve(
    query="What are the API rate limits?",
    tenant_id="my-company",
    sub_tenant_id="engineering",
    max_chunks=10
)

# List all sources
all_sources = client.sources.get_all(
    tenant_id="my-company",
    sub_tenant_id="engineering",
)

# Get specific sources by ID
specific_sources = client.sources.get_by_ids(
    tenant_id="my-company",
    sub_tenant_id="engineering",
    source_ids=["api-docs-rate-limits", "company-handbook"]
)
```

**For a more detailed explanation** of search and retrieval, including query parameters, scoring mechanisms, result structure, and advanced search features, refer to the [Search endpoint documentation](https://docs.usecortex.ai/api-reference/endpoint/search).

## SDK Method Structure & Type Safety

Our SDKs follow a predictable pattern that mirrors the API structure while providing full type safety.

> **Method Mapping** : `client.<group>.<function_name>` mirrors  `api.usecortex.ai/<group>/<function_name>`
>
> For example: `client.upload.upload_text()` corresponds to `POST /upload/upload_text`

The SDKs provide exact type parity with the API specification:

- **Request Parameters** : Every field documented in the API reference (required, optional, types, validation rules) is reflected in the SDK method signatures
- **Response Objects** : Return types match the exact JSON schema documented for each endpoint
- **Error Types** : Exception structures mirror the error response formats from the API
- **Nested Objects** : Complex nested parameters and responses maintain their full structure and typing

> This means you can rely on your IDE’s autocomplete and type checking. If a parameter is optional in the API docs, it’s optional in the SDK. If a response contains a specific field, your IDE will know about it. Our SDKs are built in such a way that your IDE will automatically provide **autocompletion, type-checking, inline documentation with examples, and compile time validation** for each and every method.
>
> Just hit **Cmd+Space/Ctrl+Space!**

## Links

- **Homepage:** [usecortex.ai](https://www.usecortex.ai/)
- **Documentation:** [docs.usecortex.ai](https://docs.usecortex.ai/)

## Our docs

Please refer to our [API reference](https://docs.usecortex.ai/api-reference/introduction) for detailed explanations of every API endpoint, parameter options, and advanced use cases.

## Support

If you have any questions or need help, please reach out to our support team at [founders@usecortex.ai](mailto:founders@usecortex.ai).
