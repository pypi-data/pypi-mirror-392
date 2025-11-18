# UsageFlow Flask

> ⚠️ **Beta Notice**: This package is currently in beta. While we strive to maintain stability, there may be breaking changes as we continue to improve the API.

The Flask package of UsageFlow provides easy integration with Flask applications for API usage tracking and management.

## Installation

```bash
pip install usageflow-flask
```

## Quick Start

```python
from flask import Flask, jsonify
from usageflow.flask import UsageFlowMiddleware

app = Flask(__name__)

# Initialize UsageFlow middleware
UsageFlowMiddleware(
    app,
    api_key="your_api_key_here",
    whitelist_routes=["/health", "/metrics"],  # Optional: routes to skip tracking
    tracklist_routes=["/api/v1"]  # Optional: routes to track specifically
)

@app.route("/api/v1/users")
def get_users():
    return jsonify({"users": ["user1", "user2"]})

if __name__ == "__main__":
    app.run()
```

## Configuration

The middleware accepts the following parameters:

- `app`: Your Flask application instance
- `api_key`: Your UsageFlow API key
- `whitelist_routes` (optional): List of routes to skip tracking
- `tracklist_routes` (optional): List of routes to track specifically

## Features

- Automatic request tracking
- Support for whitelisting and tracklisting routes

## Development

To contribute to the project:

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

MIT License
