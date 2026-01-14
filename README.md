<div align="center">

# 🌉 Bridge MCP

### Universal PC Control for Any AI

[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-blue?style=for-the-badge&logo=python)](https://fastmcp.cloud)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python)](https://python.org)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows)

**Give any AI complete control over your Windows PC**

[Features](#-features) • [Installation](#-installation) • [Tools](#-available-tools) • [Usage](#-usage) • [Deploy](#-fastmcp-cloud) • [Contributing](#-contributing)

---

<img src="assets/demo.gif" alt="Bridge MCP Demo" width="600">

</div>

---

## 🎯 What is Bridge MCP?

Bridge MCP is a **Model Context Protocol (MCP)** server that gives **any AI** full control over a Windows PC. Whether you're using Claude, ChatGPT, Cursor, Gemini, or any other MCP-compatible AI, Bridge MCP lets you:

- 🖥️ **Control Applications** - Launch, switch, resize, close any app
- 🖱️ **Automate Input** - Mouse clicks, keyboard typing, hotkeys, scrolling
- 📸 **See the Screen** - Screenshots, UI element detection, desktop state
- 🌐 **Browse the Web** - Full Chrome automation and control
- ⚡ **Run Commands** - PowerShell, CMD, file operations
- 📋 **Manage Clipboard** - Copy, paste, clear

> **Think of it as giving your AI eyes and hands to control your computer!**

---

## ✨ Features

| Category | Tools | Description |
|----------|-------|-------------|
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
│    Any AI       │         │  FastMCP Cloud  │         │  Your Windows   │
│  (Claude, etc.) │◄───────►│  (Cloud Relay)  │◄───────►│  PC (Agent)     │
└─────────────────┘  HTTPS  └─────────────────┘   HTTP  └─────────────────┘
```

- **Cloud Relay**: Runs on FastMCP Cloud (Linux), routes commands
- **Local Agent**: Runs on your Windows PC, executes commands

## 🚀 Quick Start

### Step 1: Run Local Agent on Your Windows PC

```bash
git clone https://github.com/BarhamAgha1/Bridge-MCP.git
cd Bridge-MCP
pip install -r requirements-local.txt
python local_agent.py
```

🎉 **New:** Open `http://localhost:8006` to see your **Live Dashboard**!

### Step 2: Expose Your Agent (for remote access)

Option A - Using ngrok:
```bash
ngrok http 8006
```

Option B - Port forwarding on your router (advanced)

### Step 3: Register Your Agent

In your AI conversation with Bridge MCP:
```
Use register_agent with:
- agent_id: "my-pc"
- callback_url: "https://xxxx.ngrok.io" (from ngrok)
- agent_name: "My Windows PC"
```

### Step 4: Start Controlling!

Now use any tool like `screenshot()`, `click()`, `type_text()`, etc.

---

## 🔧 Configuration

### Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bridge-mcp": {
      "command": "python",
      "args": ["path/to/Bridge-MCP/bridge_mcp.py"]
    }
  }
}
```

### Cursor

Add to your MCP settings in Cursor preferences with the same configuration.

### VS Code + Claude Code

Create `.vscode/mcp.json` in your project:

```json
{
  "mcpServers": {
    "bridge-mcp": {
      "command": "python",
      "args": ["path/to/Bridge-MCP/bridge_mcp.py"]
    }
  }
}
```

---

## 🛠️ Available Tools

<details>
<summary><b>🚀 App Control Tools</b></summary>

| Tool | Description | Example |
|------|-------------|---------|
| `app_launch` | Launch an application | `app_launch("notepad")` |
| `app_switch` | Switch to open app | `app_switch("Chrome")` |
| `app_close` | Close an application | `app_close("notepad")` |
| `app_list` | List all open apps | `app_list()` |
| `app_resize` | Resize app window | `app_resize("notepad", 800, 600)` |
| `app_minimize` | Minimize app | `app_minimize("Chrome")` |
| `app_maximize` | Maximize app | `app_maximize("Chrome")` |
| `app_move` | Move app window | `app_move("notepad", 100, 100)` |

</details>

<details>
<summary><b>🖱️ Input Tools (Mouse & Keyboard)</b></summary>

| Tool | Description | Example |
|------|-------------|---------|
| `click` | Click at coordinates | `click(500, 300)` |
| `double_click` | Double-click | `double_click(500, 300)` |
| `right_click` | Right-click | `right_click(500, 300)` |
| `type_text` | Type text | `type_text("Hello World!")` |
| `type_at` | Click and type | `type_at(500, 300, "Hello")` |
| `press_key` | Press a key | `press_key("enter")` |
| `hotkey` | Keyboard shortcut | `hotkey("ctrl", "c")` |
| `scroll` | Scroll | `scroll("down", 3)` |
| `drag` | Drag and drop | `drag(100, 100, 500, 500)` |
| `move_mouse` | Move cursor | `move_mouse(500, 300)` |

</details>

<details>
<summary><b>📸 Screen Tools</b></summary>

| Tool | Description | Example |
|------|-------------|---------|
| `screenshot` | Take screenshot | `screenshot()` |
| `get_desktop_state` | Get full desktop state | `get_desktop_state()` |
| `get_screen_size` | Get screen dimensions | `get_screen_size()` |
| `get_mouse_position` | Get cursor position | `get_mouse_position()` |
| `find_element` | Find UI element | `find_element("Submit")` |
| `get_pixel_color` | Get pixel color | `get_pixel_color(500, 300)` |
| `wait_for_element` | Wait for element | `wait_for_element("OK", 10)` |

</details>

<details>
<summary><b>⚡ System Tools</b></summary>

| Tool | Description | Example |
|------|-------------|---------|
| `run_powershell` | Run PowerShell | `run_powershell("Get-Process")` |
| `run_cmd` | Run CMD command | `run_cmd("dir")` |
| `file_read` | Read file | `file_read("C:/test.txt")` |
| `file_write` | Write file | `file_write("C:/test.txt", "Hello")` |
| `file_list` | List directory | `file_list("C:/Users")` |
| `file_exists` | Check if exists | `file_exists("C:/test.txt")` |
| `get_system_info` | System information | `get_system_info()` |
| `notification` | Show notification | `notification("Title", "Message")` |

</details>

<details>
<summary><b>🌐 Browser Tools (Chrome)</b></summary>

| Tool | Description | Example |
|------|-------------|---------|
| `chrome_open` | Open Chrome | `chrome_open("https://google.com")` |
| `chrome_new_tab` | New tab | `chrome_new_tab("https://github.com")` |
| `chrome_close_tab` | Close tab | `chrome_close_tab()` |
| `chrome_navigate` | Go to URL | `chrome_navigate("https://example.com")` |
| `chrome_back` | Go back | `chrome_back()` |
| `chrome_forward` | Go forward | `chrome_forward()` |
| `chrome_refresh` | Refresh page | `chrome_refresh()` |
| `chrome_get_url` | Get current URL | `chrome_get_url()` |
| `chrome_get_tabs` | List all tabs | `chrome_get_tabs()` |
| `chrome_switch_tab` | Switch tab | `chrome_switch_tab(2)` |
| `chrome_search` | Google search | `chrome_search("Bridge MCP")` |
| `chrome_scroll` | Scroll page | `chrome_scroll("down", 5)` |
| `scrape_page` | Scrape page | `scrape_page()` |

</details>

<details>
<summary><b>📋 Clipboard Tools</b></summary>

| Tool | Description | Example |
|------|-------------|---------|
| `clipboard_copy` | Copy to clipboard | `clipboard_copy("Hello")` |
| `clipboard_paste` | Get clipboard | `clipboard_paste()` |
| `clipboard_clear` | Clear clipboard | `clipboard_clear()` |

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

### Example 2: Take a Screenshot and Describe It

```
User: What's on my screen right now?

AI uses:
1. screenshot()
2. [AI analyzes the image and describes what it sees]
```

### Example 3: Search Something on Google

```
User: Search for "FastMCP documentation" on Google

AI uses:
1. chrome_open()
2. chrome_navigate("https://google.com")
3. type_text("FastMCP documentation")
4. press_key("enter")
```

### Example 4: Automate a Form

```
User: Fill out the login form with username "test" and password "123"

AI uses:
1. screenshot() - to see the form
2. find_element("Username")
3. click(x, y)
4. type_text("test")
5. press_key("tab")
6. type_text("123")
7. find_element("Login")
8. click(x, y)
```

---

## ☁️ FastMCP Cloud

Bridge MCP is designed to be deployed on [FastMCP Cloud](https://fastmcp.cloud) for easy access:

1. **Fork this repository**
2. **Go to** [fastmcp.cloud](https://fastmcp.cloud)
3. **Sign in** with GitHub
4. **Create project** from your forked repo
5. **Set entrypoint:** `bridge_mcp.py`
6. **Deploy!**

Your MCP will be available at: `https://your-project.fastmcp.app/mcp`

---

## 🏗️ Project Structure

```
Bridge-MCP/
├── bridge_mcp.py          # Main FastMCP server
├── tools/
│   ├── __init__.py
│   ├── app_tools.py       # App control tools
│   ├── input_tools.py     # Mouse & keyboard tools
│   ├── screen_tools.py    # Screenshot & vision tools
│   ├── system_tools.py    # PowerShell & file tools
│   ├── browser_tools.py   # Chrome automation tools
│   └── clipboard_tools.py # Clipboard tools
├── utils/
│   ├── __init__.py
│   └── helpers.py         # Utility functions
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── LICENSE                # MIT License
└── README.md              # This file
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ideas for Contributions

- [ ] Add more browser support (Firefox, Edge)
- [ ] Add Linux support
- [ ] Add macOS support
- [ ] Add more automation tools
- [ ] Improve UI element detection
- [ ] Add OCR capabilities
- [ ] Add voice control integration

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastMCP](https://fastmcp.cloud) - The amazing MCP framework
- [Anthropic](https://anthropic.com) - For creating the MCP protocol
- [UIAutomation](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows) - Windows UI automation

---

## 👤 Author

**Barham Agha**

- GitHub: [@BarhamAgha1](https://github.com/BarhamAgha1)

---

<div align="center">

**⭐ If you find this project useful, please give it a star! ⭐**

Made with ❤️ for the AI community

</div>
