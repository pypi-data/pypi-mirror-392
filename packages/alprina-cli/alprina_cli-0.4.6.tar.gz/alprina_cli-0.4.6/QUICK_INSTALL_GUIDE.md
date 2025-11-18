# Quick Install Guide

One-line installers for Alprina CLI - the easiest way to get started!

## 🚀 Quick Install

### macOS / Linux

```bash
curl -fsSL https://api.alprina.com/install.sh | sh
```

Or the shorthand version:

```bash
curl -fsSL https://api.alprina.com/cli | sh
```

### Windows (PowerShell)

```powershell
iwr https://api.alprina.com/install.ps1 -useb | iex
```

## What Happens During Installation?

The installer will:

1. ✅ **Check Python 3.10+** - Verifies you have the right version
2. ✅ **Install pipx** - Installs pipx if not present (proper way to install CLI tools)
3. ✅ **Install Alprina CLI** - Downloads and installs from PyPI
4. ✅ **Show next steps** - Guides you through authentication

## After Installation

Get started in 3 steps:

### Step 1: Sign up & Subscribe

Visit [alprina.com/pricing](https://www.alprina.com/pricing) and choose a plan:
- **Developer**: $39/month or $390/year (save 2 months!)
- **Pro**: $49/month or $490/year (save 2 months!)
- **Team**: $99/month or $990/year (save 2 months!)
- Subscriptions managed through Polar.sh

### Step 2: Authenticate

```bash
alprina auth login
```

This opens your browser for device authorization (like GitHub CLI).

### Step 3: Start Scanning

```bash
alprina scan
```

Your subscription is automatically synced from Polar via webhooks.

> **⚠️ Important**: You need an active subscription to use Alprina CLI. The installer will guide you through the signup process.

## Features

- 🎨 **Beautiful colored output** with progress indicators
- 🔍 **Smart version detection** - upgrades if already installed
- 🛡️ **Safe installation** - uses pipx for isolation
- ❌ **No sudo required** - user-level install
- 🌍 **Cross-platform** - works on macOS, Linux, and Windows

## Requirements

- Python 3.10 or higher
- Internet connection
- curl (macOS/Linux) or PowerShell (Windows)

The installer will check these for you and provide helpful error messages if anything is missing.

## Troubleshooting

### "python3: command not found"

Install Python 3.10+ from:
- **macOS**: `brew install python@3.10`
- **Ubuntu/Debian**: `sudo apt install python3.10`
- **Windows**: https://www.python.org/downloads/

### "pipx: command not found" after installation

Restart your terminal to refresh PATH, or run:
- **bash**: `source ~/.bashrc`
- **zsh**: `source ~/.zshrc`
- **Windows**: Close and reopen PowerShell

### Permission errors

The installer uses user-level installation (no sudo). If you still get permission errors:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

## Manual Installation

If you prefer manual installation:

```bash
# Install pipx
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install Alprina CLI
pipx install alprina-cli

# Verify
alprina --version
```

## API Endpoints

The install scripts are served from these endpoints:

- `GET /install.sh` - Unix/macOS install script
- `GET /install.ps1` - Windows PowerShell script
- `GET /cli` - Shorthand for install.sh
- `GET /install` - HTML installation page

## Security

- ✅ All downloads use HTTPS
- ✅ Installs from official PyPI (https://pypi.org/project/alprina-cli/)
- ✅ Uses pipx for isolated environments
- ✅ No sudo required (user-level install)
- ✅ No arbitrary code execution from untrusted sources

## Next Steps

After installation:

1. **Authenticate**: `alprina auth login`
2. **Run your first scan**: `alprina scan`
3. **Explore commands**: `alprina --help`
4. **Check documentation**: https://docs.alprina.com
5. **Join community**: https://discord.gg/alprina

## Support

- 📚 **Documentation**: https://docs.alprina.com
- 🐛 **Issues**: https://github.com/0xShortx/Alprina/issues
- 💬 **Discord**: https://discord.gg/alprina

## Alternative Installation Methods

### Using pip (not recommended for CLI tools)
```bash
pip install alprina-cli
```

### Using pipx (recommended)
```bash
pipx install alprina-cli
```

### From source
```bash
git clone https://github.com/0xShortx/Alprina.git
cd Alprina/cli
pip install -e .
```

---

**Note**: Once your API is deployed to Render, the install URLs will work automatically!
