"""Utility functions for generating service and auth URLs from base URL."""


def generate_service_url(base_url: str) -> str:
    """
    Generate service URL from base URL.
    
    Args:
        base_url: Base URL (e.g., "https://next.akabot.io")
        
    Returns:
        Service URL with /api suffix (e.g., "https://next.akabot.io/api")
    
    Examples:
        >>> generate_service_url("https://next.akabot.io")
        'https://external-api.next.akabot.io/api'
        >>> generate_service_url("https://next.akabot.io/api")
        'https://external-api.next.akabot.io/api'
    """
    base = base_url.rstrip('/')
    # Remove any /api or /auth suffix if present
    base = base.replace('/api', '').replace('/auth', '')
    return f"https://external-api.{base.lstrip('https://')}/api"


def generate_auth_url(base_url: str) -> str:
    """
    Generate authentication URL from base URL.
    
    Args:
        base_url: Base URL (e.g., "https://next.akabot.io")
        
    Returns:
        Auth URL for OpenID Connect token endpoint
        
    Examples:
        >>> generate_auth_url("https://next.akabot.io")
        'https://auth.next.akabot.io/realms/user-agent/protocol/openid-connect/token'
        >>> generate_auth_url("https://next.akabot.io/auth")
        'https://auth.next.akabot.io/realms/user-agent/protocol/openid-connect/token'
    """
    base = base_url.rstrip('/')
    # Remove any /api or /auth suffix if present
    base = base.replace('/api', '').replace('/auth', '')
    return f"https://auth.{base.lstrip('https://')}/realms/user-agent/protocol/openid-connect/token"
