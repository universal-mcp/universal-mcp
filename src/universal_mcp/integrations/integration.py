from abc import ABC, abstractmethod
from universal_mcp.stores.store import Store
import httpx

class Integration(ABC):
    """Abstract base class for handling application integrations and authentication.
    
    This class defines the interface for different types of integrations that handle
    authentication and authorization with external services.
    
    Args:
        name: The name identifier for this integration
        store: Optional Store instance for persisting credentials and other data
    
    Attributes:
        name: The name identifier for this integration
        store: Store instance for persisting credentials and other data
    """
    def __init__(self, name: str, store: Store = None):
        self.name = name
        self.store = store

    @abstractmethod
    def authorize(self):
        """Authorize the integration.
        
        Returns:
            str: Authorization URL.
        """
        pass
    
    @abstractmethod
    def get_credentials(self):
        """Get credentials for the integration.
        
        Returns:
            dict: Credentials for the integration.
        
        Raises:
            NotAuthorizedError: If credentials are not found.
        """
        pass

    @abstractmethod
    def set_credentials(self, credentials: dict):
        """Set credentials for the integration.
        
        Args:
            credentials: Credentials for the integration.
        """
        pass



class ApiKeyIntegration(Integration):
    def __init__(self, name: str, store: Store = None, **kwargs):
        super().__init__(name, store, **kwargs)

    def get_credentials(self):
        credentials = self.store.get(self.name)
        return credentials

    def set_credentials(self, credentials: dict):
        self.store.set(self.name, credentials)

    def authorize(self):
        return {"text": "Please configure the API Key for {self.name}"}
    

class OAuthIntegration(Integration):
    def __init__(self, name: str, store: Store = None, client_id: str = None, client_secret: str = None, auth_url: str = None, token_url: str = None, scope: str = None, **kwargs):
        super().__init__(name, store, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.scope = scope

    def get_credentials(self):
        credentials = self.store.get(self.name)
        if not credentials:
            return None
        return credentials
    
    def set_credentials(self, credentials: dict):
        if not credentials or not isinstance(credentials, dict):
            raise ValueError("Invalid credentials format")
        if 'access_token' not in credentials:
            raise ValueError("Credentials must contain access_token")
        self.store.set(self.name, credentials)

    def authorize(self):
        if not all([self.client_id, self.client_secret, self.auth_url, self.token_url]):
            raise ValueError("Missing required OAuth configuration")
        
        auth_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': self.scope,
        }
        
        return {
            "url": self.auth_url,
            "params": auth_params,
            "client_secret": self.client_secret,
            "token_url": self.token_url
        }
    
    def handle_callback(self, code: str):
        if not all([self.client_id, self.client_secret, self.token_url]):
            raise ValueError("Missing required OAuth configuration")
        
        token_params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        response = httpx.post(self.token_url, data=token_params)
        response.raise_for_status()
        credentials = response.json()
        self.store.set(self.name, credentials)
        return credentials

    def refresh_token(self):
        if not all([self.client_id, self.client_secret, self.token_url]):
            raise ValueError("Missing required OAuth configuration")
        
        token_params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.credentials['refresh_token']
        }
        
        response = httpx.post(self.token_url, data=token_params)
        response.raise_for_status()
        credentials = response.json()
        self.store.set(self.name, credentials)
        return credentials