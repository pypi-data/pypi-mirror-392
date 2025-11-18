"""
Install Scripts Route - Serve installation scripts
Provides one-line install scripts for Unix/macOS and Windows
"""

from fastapi import APIRouter, Response
from pathlib import Path

router = APIRouter(tags=["Install"])

# Get the install directory path (now inside the package)
INSTALL_DIR = Path(__file__).parent.parent.parent / "install"

@router.get("/install.sh")
async def get_unix_install_script():
    """
    Serve the Unix/macOS installation script

    Usage: curl -fsSL https://api.alprina.com/install.sh | sh
    """
    script_path = INSTALL_DIR / "install.sh"

    if not script_path.exists():
        return Response(
            content="# Install script not found\necho 'Error: Install script not available'\nexit 1",
            media_type="text/plain",
            status_code=404
        )

    with open(script_path, "r") as f:
        content = f.read()

    return Response(
        content=content,
        media_type="text/x-sh",
        headers={
            "Content-Disposition": "inline; filename=install.sh",
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
        }
    )


@router.get("/install.ps1")
async def get_windows_install_script():
    """
    Serve the Windows PowerShell installation script

    Usage: iwr https://api.alprina.com/install.ps1 -useb | iex
    """
    script_path = INSTALL_DIR / "install.ps1"

    if not script_path.exists():
        return Response(
            content="# Install script not found\nWrite-Host 'Error: Install script not available' -ForegroundColor Red\nexit 1",
            media_type="text/plain",
            status_code=404
        )

    with open(script_path, "r") as f:
        content = f.read()

    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Content-Disposition": "inline; filename=install.ps1",
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
        }
    )


@router.get("/cli")
async def get_cli_install_redirect():
    """
    Shorthand URL redirect to Unix install script

    Usage: curl -fsSL https://api.alprina.com/cli | sh
    """
    # Return the same script as install.sh
    script_path = INSTALL_DIR / "install.sh"

    if not script_path.exists():
        return Response(
            content="# Install script not found\necho 'Error: Install script not available'\nexit 1",
            media_type="text/plain",
            status_code=404
        )

    with open(script_path, "r") as f:
        content = f.read()

    return Response(
        content=content,
        media_type="text/x-sh",
        headers={
            "Content-Disposition": "inline; filename=install.sh",
            "Cache-Control": "public, max-age=3600",
        }
    )


@router.get("/install")
async def get_install_instructions():
    """
    Show installation instructions (HTML page)
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Install Alprina CLI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2563eb;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .install-box {
                background: #1e293b;
                color: #e2e8f0;
                padding: 20px;
                border-radius: 6px;
                margin: 20px 0;
                font-family: 'Courier New', monospace;
                overflow-x: auto;
            }
            .install-box code {
                color: #10b981;
            }
            h2 {
                color: #334155;
                margin-top: 30px;
            }
            .note {
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }
            a {
                color: #2563eb;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Install Alprina CLI</h1>
            <p class="subtitle">AI-powered security for developers</p>

            <h2>Quick Install</h2>

            <h3>macOS / Linux</h3>
            <div class="install-box">
                <code>curl -fsSL https://api.alprina.com/install.sh | sh</code>
            </div>

            <h3>Windows (PowerShell)</h3>
            <div class="install-box">
                <code>iwr https://api.alprina.com/install.ps1 -useb | iex</code>
            </div>

            <div class="note">
                <strong>Note:</strong> Requires Python 3.10 or higher. The installer will check for you.
            </div>

            <h2>What happens during installation?</h2>
            <ol>
                <li>Checks for Python 3.10+</li>
                <li>Installs pipx (if not present)</li>
                <li>Installs Alprina CLI</li>
                <li>Shows next steps</li>
            </ol>

            <h2>After Installation</h2>

            <h3>Step 1: Sign up & Subscribe</h3>
            <p>Visit <a href="https://www.alprina.com/pricing">alprina.com/pricing</a> to choose a plan:</p>
            <ul>
                <li><strong>Developer</strong>: $39/month or $390/year (save 2 months!)</li>
                <li><strong>Pro</strong>: $49/month or $490/year (save 2 months!)</li>
                <li><strong>Team</strong>: $99/month or $990/year (save 2 months!)</li>
                <li>Subscriptions managed through Polar.sh</li>
            </ul>

            <h3>Step 2: Authenticate</h3>
            <div class="install-box">
                <code>alprina auth login</code>
            </div>
            <p>This opens your browser for device authorization (like GitHub CLI).</p>

            <h3>Step 3: Start Scanning</h3>
            <div class="install-box">
                <code>alprina scan</code>
            </div>
            <p>Your subscription is automatically synced from Polar via webhooks.</p>

            <div class="note">
                <strong>⚠️ Important:</strong> You need an active subscription to use Alprina CLI.
            </div>

            <h2>Need help?</h2>
            <p>
                📚 <a href="https://docs.alprina.com">Documentation</a><br>
                💬 <a href="https://discord.gg/alprina">Discord Community</a><br>
                🐛 <a href="https://github.com/yourusername/alprina-cli/issues">Report Issues</a>
            </p>
        </div>
    </body>
    </html>
    """

    return Response(
        content=html,
        media_type="text/html",
        headers={
            "Cache-Control": "public, max-age=3600",
        }
    )
