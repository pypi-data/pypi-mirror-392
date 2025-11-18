# Revert Gate

A local gateway server for collecting and managing agent events with Google Sheets integration.

## Features

- FastAPI-based REST API for tracking agent events
- SQLite database for event storage
- Google OAuth2 authentication
- Google Sheets integration for data export
- Simple CLI to start the server

## Installation

```bash
pip install revert-gate
```

## Usage

Start the gateway server:

```bash
revert-gate
```

The server will start on `http://0.0.0.0:5001`

## API Endpoints

- `GET /api/healthcheck` - Health check endpoint
- `POST /api/track` - Track agent events
- `GET /api/events` - Retrieve tracked events
- `GET /api/auth/google/url` - Get Google OAuth URL
- `GET /api/auth/google/callback` - OAuth callback handler

## Configuration

Set your Google OAuth credentials in `src/google_oauth.py`:

```python
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"
```

## Development

Install with dev dependencies:

```bash
pip install -e ".[dev]"
```

## License

MIT
