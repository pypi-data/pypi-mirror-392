import logging
import httpx
from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProxy, JWTVerifier
from .config import config

# Configure logging
logging.basicConfig(level=logging.INFO if config.DEBUG else logging.WARNING)
logger = logging.getLogger(__name__)

def make_type_nullable(type_def):
    """Make a type definition nullable if it isn't already."""
    if type_def is None or type_def == "null":
        return type_def
    
    if isinstance(type_def, list):
        if "null" not in type_def:
            return type_def + ["null"]
        return type_def
    else:
        return [type_def, "null"]

def make_schema_nullable(schema):
    """Recursively make a schema and all its properties nullable."""
    if not isinstance(schema, dict):
        return schema
    
    if "type" in schema and schema["type"] != "null":
        schema["type"] = make_type_nullable(schema["type"])
    
    if "properties" in schema:
        for prop_schema in schema["properties"].values():
            make_schema_nullable(prop_schema)
            
    if "items" in schema and isinstance(schema["items"], dict):
        make_schema_nullable(schema["items"])
        
    if "additionalProperties" in schema and isinstance(schema["additionalProperties"], dict):
        make_schema_nullable(schema["additionalProperties"])
        
    for key in ["allOf", "anyOf", "oneOf"]:
        if key in schema:
            for sub_schema in schema[key]:
                if isinstance(sub_schema, dict):
                    make_schema_nullable(sub_schema)
    
    return schema

def make_schemas_nullable(spec):
    """Make all schema properties nullable to handle API nulls."""
    if not isinstance(spec, dict):
        return spec
    
    if "components" in spec and "schemas" in spec["components"]:
        for schema in spec["components"]["schemas"].values():
            make_schema_nullable(schema)
            
    # Walk through paths to update response schemas
    if "paths" in spec:
        for path_item in spec["paths"].values():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
                    continue
                if not isinstance(operation, dict):
                    continue
                
                if "responses" in operation:
                    for response in operation["responses"].values():
                        if not isinstance(response, dict) or "content" not in response:
                            continue
                        for media_type in response["content"].values():
                            if "schema" in media_type:
                                make_schema_nullable(media_type["schema"])
                                
                if "requestBody" in operation and isinstance(operation["requestBody"], dict):
                    if "content" in operation["requestBody"]:
                        for media_type in operation["requestBody"]["content"].values():
                            if "schema" in media_type:
                                make_schema_nullable(media_type["schema"])
                                
    return spec

def create_mcp_server():
    if not config.FANVUE_CLIENT_ID or not config.FANVUE_CLIENT_SECRET:
        logger.warning("FANVUE_CLIENT_ID and/or FANVUE_CLIENT_SECRET not set. OAuth features will not work properly.")
    
    logger.info(f"Fetching OpenAPI spec from {config.openapi_url}")
    try:
        response = httpx.get(config.openapi_url, timeout=30.0)
        response.raise_for_status()
        openapi_spec = response.json()
        openapi_spec = make_schemas_nullable(openapi_spec)
    except Exception as e:
        logger.error(f"Failed to fetch OpenAPI spec: {e}")
        raise

    # Configure Auth
    auth = None
    if config.FANVUE_CLIENT_ID and config.FANVUE_CLIENT_SECRET:
        token_verifier = JWTVerifier(
            jwks_uri=config.jwks_uri,
            issuer=config.issuer,
        )
        
        auth = OAuthProxy(
            upstream_authorization_endpoint=config.auth_url,
            upstream_token_endpoint=config.token_url,
            upstream_client_id=config.FANVUE_CLIENT_ID,
            upstream_client_secret=config.FANVUE_CLIENT_SECRET,
            token_verifier=token_verifier,
            base_url=config.MCP_SERVER_URL,
            redirect_path="/auth/callback",
            # We can define valid scopes here if needed, or leave empty to allow any
            valid_scopes=[
                "read:self", "read:chat", "write:chat", "read:fan", 
                "read:creator", "write:creator", "read:media", 
                "write:media", "write:post", "read:insights", 
                "offline", "offline_access"
            ]
        )

    client = httpx.AsyncClient(
        base_url=config.FANVUE_API_URL,
        timeout=60.0,
        follow_redirects=True
    )

    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name="Fanvue",
        auth=auth,
    )
    
    return mcp

def main():
    mcp = create_mcp_server()
    # transport="http" enables SSE and HTTP endpoints suitable for remote or local usage with OAuth
    mcp.run(transport="http", host=config.MCP_SERVER_HOST, port=config.MCP_SERVER_PORT)

if __name__ == "__main__":
    main()

