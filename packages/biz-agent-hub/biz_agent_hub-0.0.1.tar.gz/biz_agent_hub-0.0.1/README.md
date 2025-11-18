# Biz Agent Hub – Python SDK

The **Biz Agent Hub Python SDK** provides a simple way to integrate Biz Agent Hub agents (such as Supportbot Elite) into your Python or browser applications.

With this SDK, you can:

- Initialize a `BizAgentHub` client with your credentials
- Interact with **Supportbot Elite** via a simple `query()` API
- Send messages and optional files (for example, images) to the bot
- Use the SDK from **Python**

---

## Installation
```bash
pip install biz-agent-hub
```
---

## Quick Start
### ES Modules / TypeScript
```python
from biz_agent_hub.biz_agent_hub import BizAgentHub
from biz_agent_hub.supportbot_elite import SupportbotEliteQuery

client = BizAgentHub("<your_user_id>", "<your_api_key>")

supportbot_elite_query = SupportbotEliteQuery(message="what is the color of the flower in the image?")
response = client.supportbot_elite.query(
    supportbot_elite_query
)

print(response.status_code)
print(response.json())
```

---

## API Reference
`BizAgentHub`
```python
BizAgentHub("<your_user_id>", "<your_api_key>")
```
Creates an instance of the Biz Agent Hub client.

* `userId` – Your Biz Agent Hub user identifier.

* `apiKey` – Your API key for authentication.

### Properties

* `supportbot_elite: SupportbotElite`

    Interface for interacting with the Supportbot Elite agent.
  * `supportbot_elite.query: SupportbotEliteQuery(message: str, file: Optional[File] = None, session_id: Optional[str] = None) -> Any`

    Interface for interacting with the Supportbot Elite agent.

---
`SupportbotElite`

`query(self, params: SupportbotEliteQuery) -> Any`

Send a message (and optional file) to Supportbot Elite.

```python
@dataclass
class SupportbotEliteQuery:
    message: str
    file: Optional[BinaryIO] = None  # e.g. an open file object
    session_id: Optional[str] = None
```
---
## Error Handling
The `query()` method throws an error when the underlying HTTP request fails or the server responds with an error status.
```python
from biz_agent_hub.supportbot_elite import SupportbotEliteQuery

# 1. Prepare the query object
supportbot_elite_query = SupportbotEliteQuery(
    message='Help me with my issue.',
    # Note: In Python, you typically omit optional fields if they are 
    # None/undefined, or explicitly set them to None.
    file=None,
    sessionId=None,
)

# 2. Execute the API call within a try-except block
try:
    # Synchronous call (standard Python practice unless async is explicitly used)
    response = client.supportbot_elite.query(
        supportbot_elite_query
    )
    
    # Print the response (equivalent to console.log)
    print('Response:', response)
    
except Exception as err:
    # Catch any error during the API call (equivalent to catch(err))
    # Print the error (equivalent to console.error)
    print('Supportbot Elite query failed:', err)
```

---
## Building From Source
If you are working on the SDK locally:
```bash
# Install dependencies (install uv only once)
pip install uv
uv pip install -r pyproject.toml
# Build project -> dist/ (install twine only once)
pip install twine
twine upload dist/*
```
The compiled Python code will be emitted into the `dist` directory.

---
## Support
If you encounter problems or have questions:

* Open an issue in the GitHub repository

* Include:

   * Your Python version

   * The `biz-agent-hub` version

   * A minimal code sample that reproduces the issue

This helps us diagnose and resolve problems quickly.
