# Usage

## Basic Usage

```python
from livechat_webservice import LiveChatClient

# Initialize client (will use LIVECHAT_ACCESS_TOKEN and LIVECHAT_ACCOUNT_ID from .env)
client = LiveChatClient()

# Test connection
if client.test_connection():
    print("Connected successfully!")

# Get closed threads from last 24-48 hours
threads = client.get_closed_threads(hours_min=24, hours_max=48, limit=10)

for thread in threads:
    chat_id = thread['id']
    events = client.get_thread_events(chat_id)
    phones = client.extract_phone_numbers(thread, events)
    print(f"Chat {chat_id}: phones {phones}")

# Add a tag to a chat
client.add_tag_to_thread(chat_id, "recovery")

# Remove a tag
client.remove_tag_from_thread(chat_id, "recovery")
```

## Authentication

This library uses **Personal Access Token (PAT)** authentication with Basic Auth as specified in the [LiveChat API documentation](https://platform.text.com/docs/authorization/agent-authorization#personal-access-tokens).

You need both:
- **Personal Access Token**: Generated from Developer Console
- **Account ID**: Your LiveChat account identifier

These are combined and encoded using Basic Authentication (base64 encoded `account_id:token`).

## API Methods

### `LiveChatClient(access_token=None, account_id=None, base_url=None)`

Creates a new LiveChat API client.

- `access_token`: Your LiveChat Personal Access Token. If not provided, reads from `LIVECHAT_ACCESS_TOKEN` env var.
- `account_id`: Your LiveChat Account ID. If not provided, reads from `LIVECHAT_ACCOUNT_ID` env var.
- `base_url`: API base URL. Defaults to LiveChat v3.6 API.

### `test_connection() -> bool`

Tests the connection to LiveChat API.

### `get_closed_threads(hours_min=24, hours_max=48, limit=20) -> List[Dict]`

Gets closed chat threads within the specified time window.

### `get_thread_events(chat_id) -> List[Dict]`

Gets all events (messages) for a specific chat.

### `extract_phone_numbers(chat_data, events) -> List[str]`

Extracts phone numbers from chat data and events.

### `add_tag_to_thread(chat_id, tag) -> bool`

Adds a tag to a chat thread.

### `remove_tag_from_thread(chat_id, tag) -> bool`

Removes a tag from a chat thread.