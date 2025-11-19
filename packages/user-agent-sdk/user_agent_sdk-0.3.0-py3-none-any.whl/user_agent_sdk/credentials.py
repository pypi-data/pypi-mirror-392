from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings
from user_agent_sdk.utils.url_generator import generate_auth_url


class Credentials(AuthenticationSettings):
    def __init__(self, client_id: str, client_secret: str, base_url: str):
        """
        Initialize credentials with base URL.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            base_url: Base URL (e.g., https://next.akabot.io)
                     Auth URL will be generated as: {base_url}/realms/user-agent/protocol/openid-connect/token
        """
        # Generate auth_url from base_url
        auth_url = generate_auth_url(base_url)
        super().__init__(client_id, client_secret, auth_url)
        self.base_url = base_url.rstrip('/')

