# Alprina CLI Installation Scripts

One-line installers for macOS, Linux, and Windows.

## Quick Install

### macOS / Linux

```bash
curl -fsSL https://api.alprina.com/install.sh | sh
```

### Windows (PowerShell)

```powershell
iwr https://api.alprina.com/install.ps1 -useb | iex
```

## What the installer does

1. **Checks Python 3.10+** is installed
2. **Installs pipx** (if not present) - the proper way to install CLI tools
3. **Installs/upgrades** `alprina-cli` via pipx
4. **Shows next steps** for authentication

## Manual Installation

If you prefer manual installation:

```bash
# Install pipx (if needed)
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install Alprina CLI
pipx install alprina-cli

# Verify installation
alprina --version
```

## Features

- ✅ **Automatic Python version check** (requires 3.10+)
- ✅ **pipx installation** (isolated environment per CLI tool)
- ✅ **Upgrade detection** (upgrades if already installed)
- ✅ **Beautiful output** with colors and progress indicators
- ✅ **Error handling** with helpful messages
- ✅ **Cross-platform** (macOS, Linux, Windows)

## Hosting

These scripts should be hosted at:
- `https://api.alprina.com/install.sh` (Unix/macOS)
- `https://api.alprina.com/install.ps1` (Windows)

## Testing Locally

### macOS/Linux
```bash
bash install/install.sh
```

### Windows
```powershell
.\install\install.ps1
```

## Requirements

- **Python 3.10+** (will be checked by installer)
- **pip** (usually included with Python)
- **Internet connection** (to download from PyPI)

## Troubleshooting

### "python3: command not found"
Install Python 3.10+ from:
- macOS: `brew install python@3.10`
- Ubuntu/Debian: `sudo apt install python3.10`
- Windows: https://www.python.org/downloads/

### "pipx: command not found" after installation
Restart your terminal to refresh PATH, or run:
- bash: `source ~/.bashrc`
- zsh: `source ~/.zshrc`
- Windows: Close and reopen PowerShell

### Permission errors
On Unix systems, you might need to add your user to the appropriate group or use:
```bash
python3 -m pip install --user pipx
```

## Security

These scripts:
- ✅ Use HTTPS for all downloads
- ✅ Install from official PyPI (https://pypi.org/project/alprina-cli/)
- ✅ Use pipx for isolated environments
- ❌ Do NOT require `sudo` (user-level install)
- ❌ Do NOT execute arbitrary code from untrusted sources

## Alternative Installation Methods

### pip (not recommended for CLI tools)
```bash
pip install alprina-cli
```

### pipx (recommended)
```bash
pipx install alprina-cli
```

### From source
```bash
git clone https://github.com/yourusername/alprina-cli.git
cd alprina-cli
pip install -e .
```

## Support

- 📚 **Documentation**: https://docs.alprina.com
- 🐛 **Issues**: https://github.com/yourusername/alprina-cli/issues
- 💬 **Discord**: https://discord.gg/alprina
