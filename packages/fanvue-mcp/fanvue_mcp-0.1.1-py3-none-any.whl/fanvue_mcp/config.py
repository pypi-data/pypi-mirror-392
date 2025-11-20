import os

class Config:
    FANVUE_API_URL = os.getenv("FANVUE_API_URL", "https://api.fanvue.com")
    FANVUE_AUTH_URL = os.getenv("FANVUE_AUTH_URL", "https://auth.fanvue.com")
    
    # Client ID and Secret must be provided by the user via env vars
    FANVUE_CLIENT_ID = os.getenv("FANVUE_CLIENT_ID")
    FANVUE_CLIENT_SECRET = os.getenv("FANVUE_CLIENT_SECRET")
    
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")
    
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def openapi_url(self) -> str:
        return f"{self.FANVUE_API_URL}/openapi"
        
    @property
    def auth_url(self) -> str:
        return f"{self.FANVUE_AUTH_URL}/oauth2/auth"
        
    @property
    def token_url(self) -> str:
        return f"{self.FANVUE_AUTH_URL}/oauth2/token"
        
    @property
    def jwks_uri(self) -> str:
        return f"{self.FANVUE_AUTH_URL}/.well-known/jwks.json"
        
    @property
    def issuer(self) -> str:
        return self.FANVUE_AUTH_URL

config = Config()

