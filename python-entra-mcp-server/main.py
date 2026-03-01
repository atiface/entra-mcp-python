from mcp.server.fastmcp import Context, FastMCP
from graph_factory import GraphFactory
from entra_service import EntraService
import asyncio
import time
import logging


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("mcp")

mcp = FastMCP("EntraID-Manager", stateless_http=True)

service = EntraService(GraphFactory().get_client())

@mcp.tool()
async def lookup_user(query: str):
    """
        Look up a user in Entra ID. 
        Requires 'query' (the user's name or email).
        """

    if not query:
        return "Error: You must provide a name or email to search for."
    user = await service.get_user(query)
    return {"id": user["id"], "name": user["displayName"]} if user else "User not found"

@mcp.tool()
async def get_user_groups(user_id: str):
    """
        Retrieves all Entra ID groups a specific user belongs to.
        Expects 'user_id', which is the unique GUID found via lookup_user.
        """
    return await service.list_user_groups(user_id)

@mcp.tool()
async def add_user_to_group(group_id: str, user_id: str):
    """Add a specific user to a group."""
    await service.add_member(group_id, user_id)
    return "User added successfully."

@mcp.tool()
async def manage_group(name: str, nickname: str, type: str = "security", teamify: bool = False):
    """Create a Security or M365 group and optionally enable Teams."""
    is_m365 = (type.lower() == "m365")
    group = await service.create_group(name, nickname, is_m365)
    
    msg = f"Group created: {group.id}"
    if is_m365 and teamify:
        await service.enable_teams(group.id)
        msg += " (Teams enabled)"
    return msg

@mcp.tool()
async def get_application_permissions_map():
    """
    Returns a list of applications and the Entra ID groups required to access them.
    Use this tool when a user asks for access to a specific software or platform
    to identify which group_id should be used with add_user_to_group.
    """
    return await service.get_app_access_map()






@mcp.tool()
def ping() -> str:
    t0 = time.time()
    log.debug("TOOL ping called")
    result = "pong"
    log.debug("TOOL ping returning (%d ms)", int((time.time()-t0)*1000))
    return result





async def run_http_server() -> None:
    """Run the MCP server in HTTP mode."""



    mcp.settings.port = int(8000)
    mcp.settings.host = "0.0.0.0"

        # Run the FastMCP server as HTTP endpoint
    await mcp.run_streamable_http_async()



def main() -> None:
    """Main entry point for the MCP server."""

    # Run the HTTP server
    asyncio.run(run_http_server())


if __name__ == "__main__":
    main()