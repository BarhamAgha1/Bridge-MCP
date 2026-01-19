# Visual Desktop Bridge (Claude Bridge)

**Visual Desktop Bridge - Give any AI full control over Windows**
Currently designed for **Claude Code** and **Claude Desktop**.

> [!NOTE]
> This project was formerly known as "Universal PC Control".
>
> <!-- mcp-name: barhamagha1/bridge-mcp -->

## Overview
Visual Desktop Bridge is a "body" for your AI "brain". It allows Claude to:
1.  **See your screen** (using screenshots and grid overlays).
2.  **Control your mouse/keyboard** (using coordinate grids and hotkeys).
3.  **Manage applications** (launch, switch, close).
4.  **Run locally** on your PC while communicating securely with the cloud/MCP.

## Key Features
*   **Vision-First Control**: Claude sees a grid overlay (e.g., "Click A5") to interact with any app, even those without accessibility API support (Spotify, Games, etc.).
*   **Persistent Connection**: Agents are remembered across sessions.
*   **Fast & Lightweight**: Built on `fastmcp` and optimized for low latency.
*   **Safe**: Includes a "Safety Sentinel" to block dangerous commands (like deleting files) unless explicitly approved.

## Installation

### Easy Install (Windows)
1.  Download the latest release.
2.  Run `ClaudeBridgeAgent.exe`.
3.  The agent will auto-register with your MCP configuration.

### Manual Setup (Developers)
1.  Clone the repo.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-local.txt
    ```
3.  Run the bridge server:
    ```bash
    python bridge_mcp.py
    ```
4.  Run the local agent:
    ```bash
    python local_agent.py
    ```

## Usage with Claude
Once running, you can ask Claude to:
*   "Take a screenshot and tell me what you see."
*   "Open Notepad and type 'Hello World'."
*   "Click the Play button on Spotify."
*   "Organize the files in my Downloads folder."

## Architecture
*   **Bridge Server (`bridge_mcp.py`)**: Acts as the MCP entry point for Claude.
*   **Local Agent (`local_agent.py`)**: Runs on the Windows PC, executing actual mouse/keyboard commands.
*   **Vision Engine**: Uses `pyautogui` and `PIL` to generate grid-augmented screenshots for the AI.

## Safety
By default, "Safe Mode" is ON. Dangerous commands (powershell, file writes) require user confirmation via the desktop overlay.
