"""Utility functions for client."""
from __future__ import annotations

import asyncio
import random
import string
from urllib.parse import urlparse


def normalize_server_url(server_input: str) -> str:
    """
    Convert HTTP/HTTPS URL to WebSocket URL.
    
    Examples:
        https://tunnel.example.com -> wss://tunnel.example.com
        http://localhost:8081 -> ws://localhost:8081
        wss://already.ws -> wss://already.ws (unchanged)
        ws://already.ws -> ws://already.ws (unchanged)
    """
    server_input = server_input.strip()
    
    # If already WebSocket URL, return as-is
    if server_input.startswith(("ws://", "wss://")):
        return server_input
    
    # If HTTP/HTTPS, convert to WS/WSS
    if server_input.startswith("http://"):
        return server_input.replace("http://", "ws://", 1)
    if server_input.startswith("https://"):
        return server_input.replace("https://", "wss://", 1)
    
    # If no protocol, assume HTTPS -> WSS
    if not server_input.startswith(("http://", "https://", "ws://", "wss://")):
        return f"wss://{server_input}"
    
    return server_input


def validate_subdomain(subdomain: str) -> bool:
    """
    Validate subdomain format according to DNS rules.
    
    Rules:
    - Length: 3-63 characters
    - First character must be a letter
    - Can contain letters, digits, and hyphens
    - Cannot start or end with hyphen
    """
    if not subdomain:
        return False
    
    subdomain = subdomain.strip().lower()
    
    # Length check
    if len(subdomain) < 3 or len(subdomain) > 63:
        return False
    
    # First character must be a letter
    if not subdomain[0].isalpha():
        return False
    
    # Last character cannot be a hyphen
    if subdomain[-1] == '-':
        return False
    
    # Can only contain letters, digits, and hyphens
    if not all(c.isalnum() or c == '-' for c in subdomain):
        return False
    
    # Cannot have consecutive hyphens
    if '--' in subdomain:
        return False
    
    return True


async def check_local_port(port: int, timeout: float = 2.0) -> tuple[bool, str]:
    """
    Check if local port is accessible.
    
    Returns:
        (is_accessible, error_message)
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("127.0.0.1", port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True, ""
    except asyncio.TimeoutError:
        return False, f"Port {port} is not responding (timeout)"
    except ConnectionRefusedError:
        return False, f"Port {port} is not accessible (connection refused)"
    except Exception as e:
        return False, f"Port {port} check failed: {str(e)}"


def generate_random_subdomain(length: int = 8) -> str:
    """Generate a random subdomain name."""
    chars = string.ascii_lowercase + string.digits
    # First char must be letter
    first = random.choice(string.ascii_lowercase)
    rest = ''.join(random.choice(chars) for _ in range(length - 1))
    return f"{first}{rest}"

