# 🌉 Bridge MCP

### Universal PC Control for Any AI

[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-blue?style=for-the-badge&logo=python)](https://fastmcp.cloud)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python)](https://python.org)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows)

**Give any AI complete control over your Windows PC**

[Features](#-features) • [Quick Start](#-quick-start) • [Configuration](#-configuration) • [Tools](#-available-tools) • [Troubleshooting](#-troubleshooting) • [Contributing](#-contributing)

---

## 🎯 What is Bridge MCP?

Bridge MCP is a **Model Context Protocol (MCP)** server that gives **any AI** full control over a Windows PC. Whether you're using Claude, ChatGPT, Cursor, Gemini, or any other MCP-compatible AI, Bridge MCP lets you:

* 🖥️ **Control Applications** - Launch, switch, resize, close any app
* 🖱️ **Automate Input** - Mouse clicks, keyboard typing, hotkeys, scrolling
* 📸 **See the Screen** - Screenshots, UI element detection, desktop state
* 🌐 **Browse the Web** - Full Chrome automation and control
* ⚡ **Run Commands** - PowerShell, CMD, file operations
* 📋 **Manage Clipboard** - Copy, paste, clear

> **Think of it as giving your AI eyes and hands to control your computer!**

---

## ✨ Features

| Category | Tools | Description |
| --- | --- | --- |
| 🚀 **App Control** | 8 tools | Launch, switch, close, resize, minimize, maximize applications |
| 🖱️ **Mouse & Keyboard** | 10 tools | Click, type, hotkeys, scroll, drag, move cursor |
| 📸 **Screen Capture** | 7 tools | Screenshots, desktop state, find UI elements |
| ⚡ **System** | 8 tools | PowerShell, CMD, file read/write, system info |
| 🌐 **Browser** | 15 tools | Chrome control, tabs, navigation, web scraping |
| 📋 **Clipboard** | 3 tools | Copy, paste, clear clipboard |
| 🔧 **Utilities** | 5+ tools | Wait, dialogs, action sequences |

**Total: 40+ powerful tools for complete PC automation!**

---

## 🏗️ Architecture

Bridge MCP uses a **Relay Architecture** to work across platforms:
```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    Any AI       │         │  Cloud Relay    │         │  Your Windows   │
│  (Claude, etc.) │◄───────►│  (bridge_mcp)   │◄───────►│  PC (Agent)     │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

* **bridge_mcp.py** - MCP server (runs locally or on FastMCP Cloud)
* **local_agent.py** - HTTP server on your PC that executes commands (port 8006)

---

## 🚀 Quick Start

### Step 1: Clone the Repository
```bash
git clone https://github.com/BarhamAgha1/Bridge-MCP.git
cd Bridge-MCP
```

### Step 2: Install Dependencies
```bash
pip install -r requirements-local.txt
```

### Step 3: Start the Local Agent
```bash
python local_agent.py
```

Keep this terminal open! The agent will display:
```
Bridge MCP Local Agent running on http://127.0.0.1:8006
```

### Step 4: Configure Your AI Client

See [Configuration](#-configuration) below for Claude Desktop, Cursor, or VS Code setup.

### Step 5: Register Your Agent

In your AI conversation, register the local agent:
```
Use register_agent with:
- agent_id: "my-pc"
- callback_url: "http://127.0.0.1:8006"
- agent_name: "My Windows PC"
```

### Step 6: Start Controlling!

Now use any tool like `screenshot()`, `click(100, 200)`, `type_text("Hello")`, `app_launch("notepad")`, etc.

---

## 🔧 Configuration

### Claude Desktop

1. Open the config file at `%APPDATA%\Claude\claude_desktop_config.json`

2. Add Bridge MCP:
```json
{
  "mcpServers": {
    "bridge-mcp": {
      "command": "python",
      "args": ["C:\\Users\\YourName\\Path\\To\\Bridge-MCP\\bridge_mcp.py"]
    }
  }
}
```

⚠️ **Important:** Replace the path with the **actual location** where you cloned the repository!

**Example paths:**
- `C:\\Users\\PC\\Desktop\\Bridge-MCP\\bridge_mcp.py`
- `D:\\Projects\\Bridge-MCP\\bridge_mcp.py`

3. **Restart Claude Desktop completely** (close and reopen)

### Cursor

Add to your MCP settings in Cursor preferences with the same configuration format.

### VS Code + Claude Code

Create `.vscode/mcp.json` in your project:
```json
{
  "mcpServers": {
    "bridge-mcp": {
      "command": "python",
      "args": ["C:\\Users\\YourName\\Path\\To\\Bridge-MCP\\bridge_mcp.py"]
    }
  }
}
```

### Remote Access (Optional)

To control your PC from anywhere, expose the local agent with ngrok:
```bash
ngrok http 8006
```

Then use the ngrok URL (e.g., `https://xxxx.ngrok.io`) as your callback_url when registering.

---

## 🛠️ Available Tools

<details>
<summary><b>🚀 App Control Tools</b></summary>

| Tool | Description | Example |
| --- | --- | --- |
| `app_launch` | Launch an application | `app_launch("notepad")` |
| `app_switch` | Switch to open app | `app_switch("Chrome")` |
| `app_close` | Close an application | `app_close("notepad")` |
| `app_list` | List all open apps | `app_list()` |

</details>

<details>
<summary><b>🖱️ Input Tools (Mouse & Keyboard)</b></summary>

| Tool | Description | Example |
| --- | --- | --- |
| `click` | Click at coordinates | `click(500, 300)` |
| `double_click` | Double-click | `double_click(500, 300)` |
| `right_click` | Right-click | `right_click(500, 300)` |
| `type_text` | Type text | `type_text("Hello World!")` |
| `press_key` | Press a key | `press_key("enter")` |
| `hotkey` | Keyboard shortcut | `hotkey("ctrl,c")` |
| `scroll` | Scroll | `scroll("down", 3)` |
| `drag` | Drag and drop | `drag(100, 100, 500, 500)` |
| `move_mouse` | Move cursor | `move_mouse(500, 300)` |

</details>

<details>
<summary><b>📸 Screen Tools</b></summary>

| Tool | Description | Example |
| --- | --- | --- |
| `screenshot` | Take screenshot | `screenshot()` |
| `get_desktop_state` | Get full desktop state | `get_desktop_state()` |
| `get_screen_size` | Get screen dimensions | `get_screen_size()` |
| `get_mouse_position` | Get cursor position | `get_mouse_position()` |

</details>

<details>
<summary><b>⚡ System Tools</b></summary>

| Tool | Description | Example |
| --- | --- | --- |
| `run_powershell` | Run PowerShell | `run_powershell("Get-Process")` |
| `run_cmd` | Run CMD command | `run_cmd("dir")` |
| `file_read` | Read file | `file_read("C:/test.txt")` |
| `file_write` | Write file | `file_write("C:/test.txt", "Hello")` |
| `file_list` | List directory | `file_list("C:/Users")` |

</details>

<details>
<summary><b>🌐 Browser Tools (Chrome)</b></summary>

| Tool | Description | Example |
| --- | --- | --- |
| `chrome_open` | Open Chrome | `chrome_open("https://google.com")` |
| `chrome_navigate` | Go to URL | `chrome_navigate("https://example.com")` |

</details>

<details>
<summary><b>📋 Clipboard Tools</b></summary>

| Tool | Description | Example |
| --- | --- | --- |
| `clipboard_copy` | Copy to clipboard | `clipboard_copy("Hello")` |
| `clipboard_paste` | Get clipboard | `clipboard_paste()` |

</details>

---

## 💡 Usage Examples

### Example 1: Open Notepad and Write Text
```
User: Open notepad and write "Hello from AI!"

AI uses:
1. app_launch("notepad")
2. wait(1)
3. type_text("Hello from AI!")
```

### Example 2: Take a Screenshot
```
User: What's on my screen right now?

AI uses:
1. screenshot()
2. [AI analyzes the image and describes what it sees]
```

### Example 3: Search on Google
```
User: Search for "Bridge MCP" on Google

AI uses:
1. chrome_open("https://google.com")
2. type_text("Bridge MCP")
3. press_key("enter")
```

---

## 🔧 Troubleshooting

### Claude Desktop shows "Server disconnected"

1. **Check the path** - Make sure the path in your config points to the actual `bridge_mcp.py` file. The path must be absolute and use double backslashes (`\\`) in JSON.

2. **Test manually** - Open Command Prompt and run:
```cmd
   cd "C:\path\to\Bridge-MCP"
   python bridge_mcp.py
```
   It should stay running (not exit immediately). Press Ctrl+C to stop.

3. **Install dependencies**:
```cmd
   pip install fastmcp httpx
```

4. **Restart Claude Desktop** - Fully close and reopen after any config changes.

### Local agent not receiving commands

1. Make sure `local_agent.py` is running in a terminal (keep it open!)
2. Verify the callback URL is correct when registering the agent
3. For local use: `http://127.0.0.1:8006`
4. For remote access: Use ngrok (`ngrok http 8006`) and use the ngrok URL

### "No agents connected" error

You need to register your local agent first:
```
register_agent("my-pc", "http://127.0.0.1:8006", "My PC")
```

### Unicode/Emoji errors on Windows

If `local_agent.py` crashes with Unicode errors, the terminal may not support emojis. This has been fixed in the latest version.

---

## ☁️ FastMCP Cloud Deployment

Bridge MCP can be deployed on [FastMCP Cloud](https://fastmcp.cloud) for easy access:

1. Fork this repository
2. Go to [fastmcp.cloud](https://fastmcp.cloud)
3. Sign in with GitHub
4. Create project from your forked repo
5. Set entrypoint: `bridge_mcp.py`
6. Deploy!

Your MCP will be available at: `https://your-project.fastmcp.app/mcp`

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ideas for Contributions

* Add more browser support (Firefox, Edge)
* Add Linux support
* Add macOS support
* Add more automation tools
* Improve UI element detection
* Add OCR capabilities

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

* [FastMCP](https://fastmcp.cloud) - The amazing MCP framework
* [Anthropic](https://anthropic.com) - For creating the MCP protocol

---

## 👤 Author

**Barham Agha**

* GitHub: [@BarhamAgha1](https://github.com/BarhamAgha1)

---

**⭐ If you find this project useful, please give it a star! ⭐**

Made with ❤️ for the AI community
