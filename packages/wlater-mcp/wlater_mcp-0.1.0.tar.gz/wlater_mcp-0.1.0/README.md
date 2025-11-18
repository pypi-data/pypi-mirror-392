# wlater MCP Server

Connect your AI assistant to Google Keep. Search, read, and manage your notes and lists through natural conversation.

## Installation

```bash
pip install wlater-mcp
```

## Setup

Run the setup wizard to configure your credentials:

```bash
wlater-setup
```

Choose your authentication method:
- **Automated**: Opens Chrome and logs you in automatically
- **Manual**: Enter your credentials directly

## Configuration

Add to your MCP client's config file (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "wlater": {
      "command": "python",
      "args": ["-m", "wlater_mcp.server"]
    }
  }
}
```

Restart your AI assistant and you're ready!

## Usage

Talk to your AI naturally:

- "Show me all my pinned notes"
- "What's on my shopping list?"
- "Check off 'buy milk' from my grocery list"
- "Create a note called 'Meeting Notes'"
- "Add 'call dentist' to my todo list"
- "Find notes labeled 'work'"

All changes are previewed before being saved to Google Keep.

## Features

- ✅ Read and search your Keep notes
- ✅ Manage todo lists (check/uncheck items)
- ✅ Create notes and lists
- ✅ Add labels and change colors
- ✅ Preview changes before syncing
- ✅ Secure credential storage (OS keyring)
- ❌ Cannot delete notes (safety feature)

## Troubleshooting

**"Master token not found"**
```bash
wlater-setup
```

**"Authentication failed"**  
Your token may have expired. Re-run setup.

**Server not appearing**  
Check your config file paths and restart your MCP client.

## Security

- Credentials stored in your system keyring (Windows Credential Locker, macOS Keychain, Linux Secret Service)
- Preview all changes before syncing
- No automatic modifications
- Delete operations not exposed

## Links

- [GitHub Repository](https://github.com/briansbrian/wlater-McpServer)
- [Report Issues](https://github.com/briansbrian/wlater-McpServer/issues)
- [Model Context Protocol](https://modelcontextprotocol.io)

## License

MIT License - See [LICENSE](LICENSE) for details
