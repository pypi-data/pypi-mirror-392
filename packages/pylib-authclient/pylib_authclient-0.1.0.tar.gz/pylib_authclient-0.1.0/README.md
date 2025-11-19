# pyauthclient

OAuth2 helpers

## Installation

```bash
pip install pyauthclient
```

## 💡 Usage Examples

### Basic Operations

```python
from pylib_authclient import OAuthClient

# OAuth client
client = OAuthClient(client_id, client_secret)
token = client.get_access_token()
# Use token for authenticated requests
```

### AI/ML Use Cases

```python
from pylib_authclient import OAuthClient

# Authenticate AI API calls
oauth = OAuthClient(api_key, api_secret)
token = oauth.authenticate()
headers = {"Authorization": f"Bearer {token}"}
```

## 📚 API Reference

See package documentation for complete API reference.


## 🤖 AI Agent Friendly

This package is optimized for AI agents and code generation tools:
- **Clear function names** and signatures
- **Comprehensive docstrings** with examples
- **Type hints** for better IDE support
- **Common use cases** documented
- **Zero dependencies** for reliability

## License

MIT
