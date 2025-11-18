import os
import keyring
from typing import Optional

SERVICE_NAME = "textmine"
TOKEN_KEY = "session_token"


def get_server_url() -> str:
    """Get server URL from environment or use default."""
    return os.getenv("TEXTMINE_SERVER", "https://workspace.g062.repl.co")


def save_session(token: str) -> None:
    """Save session token securely using keyring."""
    keyring.set_password(SERVICE_NAME, TOKEN_KEY, token)


def get_session() -> Optional[str]:
    """Retrieve session token from keyring."""
    return keyring.get_password(SERVICE_NAME, TOKEN_KEY)


def clear_session() -> None:
    """Delete stored session token."""
    try:
        keyring.delete_password(SERVICE_NAME, TOKEN_KEY)
    except keyring.errors.PasswordDeleteError:
        pass
