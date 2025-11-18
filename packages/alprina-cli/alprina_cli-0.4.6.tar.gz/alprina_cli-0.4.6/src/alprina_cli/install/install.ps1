# Alprina CLI Installation Script for Windows
# Usage: iwr https://api.alprina.com/install.ps1 -useb | iex

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-ColorOutput Cyan "╔═══════════════════════════════════════╗"
Write-ColorOutput Cyan "║     Alprina CLI Installation          ║"
Write-ColorOutput Cyan "║   AI-Powered Security for Developers  ║"
Write-ColorOutput Cyan "╚═══════════════════════════════════════╝"
Write-Host ""

Write-Host "Checking system requirements..." -ForegroundColor White

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]

        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-ColorOutput Red "❌ Python 3.10+ is required (found Python $major.$minor)"
            Write-Host ""
            Write-Host "Please install Python 3.10 or higher from:"
            Write-Host "  https://www.python.org/downloads/"
            Write-Host ""
            Write-Host "Make sure to check 'Add Python to PATH' during installation!"
            exit 1
        }

        Write-ColorOutput Green "✓ Python $major.$minor found"
    }
} catch {
    Write-ColorOutput Red "❌ Python is not installed or not in PATH"
    Write-Host ""
    Write-Host "Please install Python 3.10 or higher from:"
    Write-Host "  https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation!"
    exit 1
}

# Check if pipx is installed
$pipxInstalled = $false
try {
    pipx --version | Out-Null
    $pipxInstalled = $true
    Write-ColorOutput Green "✓ pipx found"
} catch {
    Write-ColorOutput Yellow "⚠ pipx not found. Installing pipx..."

    try {
        python -m pip install --user pipx
        python -m pipx ensurepath

        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")

        Write-ColorOutput Green "✓ pipx installed"
        Write-ColorOutput Yellow "⚠ Please restart your terminal after installation completes"
        $pipxInstalled = $true
    } catch {
        Write-ColorOutput Red "❌ Failed to install pipx"
        Write-Host ""
        Write-Host "Please install pipx manually:"
        Write-Host "  python -m pip install --user pipx"
        Write-Host "  python -m pipx ensurepath"
        exit 1
    }
}

# Install/Upgrade Alprina CLI
Write-Host ""
Write-Host "Installing Alprina CLI..." -ForegroundColor White

try {
    $existingInstall = pipx list 2>&1 | Select-String "alprina-cli"

    if ($existingInstall) {
        Write-Host "Upgrading existing installation..."
        pipx upgrade alprina-cli
    } else {
        Write-Host "Installing Alprina CLI..."
        pipx install alprina-cli
    }

    Write-Host ""
    Write-ColorOutput Green "✓ Alprina CLI installed successfully!"
    Write-Host ""

    Write-ColorOutput Cyan "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-ColorOutput Cyan "         Getting Started with Alprina      "
    Write-ColorOutput Cyan "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""

    Write-Host "Step 1: Sign up & Subscribe" -ForegroundColor White
    Write-Host "  Visit: " -NoNewline
    Write-Host "https://www.alprina.com/pricing" -ForegroundColor Cyan
    Write-Host "  Plans: Developer (`$39/mo), Pro (`$49/mo), Team (`$99/mo)"
    Write-Host "  💰 Save 2 months with annual billing!"
    Write-Host ""

    Write-Host "Step 2: Authenticate" -ForegroundColor White
    Write-Host "  Run: " -NoNewline
    Write-Host "alprina auth login" -ForegroundColor Green
    Write-Host "  This will open your browser to authorize the CLI"
    Write-Host ""

    Write-Host "Step 3: Start Scanning" -ForegroundColor White
    Write-Host "  Run: " -NoNewline
    Write-Host "alprina scan" -ForegroundColor Green
    Write-Host "  Start securing your code with AI-powered analysis"
    Write-Host ""

    Write-ColorOutput Yellow "⚠ Important: You need an active subscription to use Alprina CLI"
    Write-ColorOutput Yellow "  Visit https://www.alprina.com/pricing to get started"
    Write-Host ""

    Write-ColorOutput Cyan "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""

    Write-ColorOutput Cyan "Need help? Visit https://docs.alprina.com"
    Write-ColorOutput Cyan "Questions? Join our Discord: https://discord.gg/alprina"
    Write-Host ""

    # Try to show version
    try {
        $version = alprina --version 2>&1 | Select-String -Pattern "version (\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
        Write-ColorOutput Green "Installed version: $version"
    } catch {
        Write-ColorOutput Yellow "⚠ Please restart your terminal to use 'alprina' command"
    }

} catch {
    Write-ColorOutput Red "❌ Installation failed: $_"
    Write-Host ""
    Write-Host "Please try manual installation:"
    Write-Host "  pip install alprina-cli"
    exit 1
}
