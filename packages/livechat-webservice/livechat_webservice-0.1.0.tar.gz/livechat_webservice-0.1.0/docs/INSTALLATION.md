# Installation

## Requirements

- Python 3.12+
- A LiveChat Personal Access Token (PAT)
- Your LiveChat Account ID

## Install from source

```bash
git clone https://github.com/patitas-and-co/livechat-webservice.git
cd livechat-webservice
pip install -e .
```

## Install from PyPI (when available)

```bash
pip install livechat-webservice
```

## Configuration

### Generate a Personal Access Token

1. Go to [LiveChat Developer Console](https://platform.text.com/console/)
2. Navigate to Settings > Authorization > Personal Access Tokens
3. Create a new token with the necessary scopes for your use case
4. Copy your Account ID from the Developer Console

### Set up environment variables

Create a `.env` file in your project root:

```env
LIVECHAT_ACCESS_TOKEN=your_personal_access_token_here
LIVECHAT_ACCOUNT_ID=your_account_id_here
```

Or pass the credentials directly when creating the client:

```python
from livechat_webservice import LiveChatClient

client = LiveChatClient(
    access_token="your_token",
    account_id="your_account_id"
)
```