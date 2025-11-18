"""
MCP Computer Use Server

Provides computer control tools for AI agents, including browser control
and system automation capabilities.
"""

from fastmcp import FastMCP

from .tools import app_launcher, browser, credential_typing, credentials

mcp = FastMCP("MCP Computer Use Server")


# Register browser control tools
mcp.tool()(browser.open_browser)

# Note: Commented out redundant browser tools - testing showed no behavioral difference
# from open_browser(). Keeping implementations in browser.py for potential future use.
# If needed, uncomment these lines to re-enable:
# mcp.tool()(browser.open_browser_new_tab)
# mcp.tool()(browser.open_browser_new_window)

# Register credential management tools
mcp.tool()(credentials.get_credentials)
mcp.tool()(credential_typing.type_credential_field)

# Register application launcher tools
mcp.tool()(app_launcher.open_application)
mcp.tool()(app_launcher.verify_application)
