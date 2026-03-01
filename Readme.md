# Entra ID Management - MCP & Copilot Agent

This project provides a **Declarative Copilot Agent** powered by a **Python MCP (Model Context Protocol) Server**. It allows administrators to manage Entra ID users and group-based application access using natural language through Microsoft Teams.

## 1. System Architecture

The solution uses a multi-layered approach to bridge the gap between LLM reasoning and secure identity management.



1.  **Copilot Agent:** The user interface (Teams/Microsoft 365) that interprets intent.
2.  **MCP Server (Python):** A Starlette-based server that exposes specific tools (User Lookup, Group Addition).
3.  **Dev Tunnel:** Provides a secure HTTPS relay from the public internet to your local machine.
4.  **Microsoft Graph API:** The engine that performs the actual changes in Entra ID.
5.  **Entra ID:** The identity provider containing your users and groups.

---

## 2. Configure Entra ID App Registration

The Python server requires an Identity to talk to the Graph API.

1.  Log in to the [Azure Portal](https://portal.azure.com) and navigate to **Microsoft Entra ID**.
2.  Go to **App registrations** > **New registration**.
    * **Name:** `Entra-MCP-Server`
    * **Supported account types:** Accounts in this organizational directory only.
3.  **Authentication:** No Redirect URI is needed for this service-to-service flow.
4.  **Certificates & Secrets:**
    * Go to **Client secrets** > **New client secret**.
    * **Copy the Value** immediately (you won't see it again).
5.  **API Permissions:**
    * Click **Add a permission** > **Microsoft Graph** > **Application permissions**.
    * Add: `User.Read.All`, `GroupMember.ReadWrite.All`, `Directory.Read.All`.
    * **Important:** Click **Grant admin consent for [Your Org]**.

---

## 3. Running the Python MCP Server

You can run the server using standard Python or the high-performance `uv` package manager.

### Option A: Using UV (Recommended)
```powershell
# Install dependencies
uv sync

# Run the server
uv run main.py
```

## 4 Local Testing with MCP Inspector
------------------------------------

Before connecting to Copilot, use the **MCP Inspector** to verify your tools are working correctly.

1.  PowerShellnpm install -g @modelcontextprotocol/inspector
    
2.  PowerShellnpx @modelcontextprotocol/inspector http://localhost:8000/sse
    
3.  **Test the Tools:**
    
    *   In the browser window that opens, select the lookup\_user tool.
        
    *   Provide a test name (e.g., "Jane Doe").
        
    *   Verify you receive a JSON response with the User ID.
        

## 5 Connecting Copilot Agent to MCP
-----------------------------------

1.  PowerShelldevtunnel host -p 8000 --allow-anonymous_Copy the provided .devtunnels.ms URL._
    
2.  JSON"capabilities": \[ { "name": "mcp-server", "mcp\_endpoint": "\[https://YOUR-TUNNEL-ID.devtunnels.ms/sse\](https://YOUR-TUNNEL-ID.devtunnels.ms/sse)" }\]
    
3.  **Provision via Teams Toolkit:**
    
    *   Open **VS Code**.
        
    *   Click the **Teams Toolkit** icon in the sidebar.
        
    *   Under **Lifecycle**, click **Provision**.
        
    *   Once finished, press **F5** to launch the agent in Teams.
        
4.  **Chat with the Agent:**In Copilot agent, select your new agent and type: _"Find user Jane Smith and tell me what groups she is in."_