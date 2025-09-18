#!/usr/bin/env python3
"""
Credentials Wrapper for MCP Servers
Uses centralized credentials_manager.py for all credential management

JTBD: Как MCP сервер, я хочу получать credentials через единую систему,
чтобы обеспечить консистентность и избежать дублирования кода.

TDD Documentation Standard v2.5 Compliance:
- Uses existing credentials_manager.py (DRY principle)
- Simple wrapper around centralized system
- No code duplication
"""

import sys
import os
from pathlib import Path

import sys
from pathlib import Path

# Add the heroes_platform directory to Python path
heroes_platform_path = Path(__file__).parent.parent
if str(heroes_platform_path) not in sys.path:
    sys.path.insert(0, str(heroes_platform_path))

try:
    from shared.credentials_manager import credentials_manager  # type: ignore
except ImportError:
    # Fallback for relative import issues
    import importlib.util
    spec = importlib.util.spec_from_file_location("credentials_manager", 
                                                 heroes_platform_path / "shared" / "credentials_manager.py")
    if spec and spec.loader:
        credentials_manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(credentials_manager_module)
        credentials_manager = credentials_manager_module.credentials_manager
    else:
        # Ultimate fallback - create empty credentials manager
        credentials_manager = type('CredentialsManager', (), {
            'get_credentials': lambda service: {},
            'set_credentials': lambda service, creds: None
        })()

def get_service_credentials(service: str) -> dict:
    """Get all credentials for a service using centralized manager"""
    
    # Service to credential mapping
    service_credentials = {
        "telegram": ["telegram_api_id", "telegram_api_hash", "telegram_session"],
        "n8n": ["N8N_API_KEY", "N8N_API_URL"],
        "playwright": ["PLAYWRIGHT_BROWSER_TOKEN"],
        "hh": ["hh_oauth_client_id", "hh_oauth_client_secret"],
        "google": ["google_service_account_json"],  # Use Service Account JSON for Google Sheets MCP
        "google_oauth": ["google_oauth_client_id", "google_oauth_client_secret", "google_refresh_token"],  # OAuth for other Google services
        "linear": ["linear_api_key"]
    }
    
    if service not in service_credentials:
        print(f"ERROR: Unknown service: {service}", file=sys.stderr)
        print(f"Available services: {', '.join(service_credentials.keys())}", file=sys.stderr)
        return {}
    
    credentials = {}
    # Silent credential loading to avoid JSON-RPC interference
    for credential_name in service_credentials[service]:
        result = credentials_manager.get_credential(credential_name)
        if result.success:
            # Map credential name to environment variable name
            env_var = credential_name.upper()
            credentials[env_var] = result.value
        # Silent failure - credentials will be empty if not found
    
    return credentials

def main() -> int:
    """Main wrapper function"""
    if len(sys.argv) < 3:
        print("Usage: python credentials_wrapper.py SERVICE COMMAND [ARGS...]", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  python credentials_wrapper.py telegram python main.py", file=sys.stderr)
        print("  python credentials_wrapper.py n8n node dist/mcp/index.js", file=sys.stderr)
        return 1
    
    service = sys.argv[1]
    command = sys.argv[2]
    args = sys.argv[3:]
    
    # Get credentials using centralized manager
    credentials = get_service_credentials(service)
    
    # Set environment variables
    for key, value in credentials.items():
        os.environ[key] = value
    
    # Run command
    print(f"🚀 Starting {command} {' '.join(args)}...", file=sys.stderr)
    
    import subprocess
    try:
        # For MCP servers, we need to preserve stdin/stdout for JSON-RPC
        # but redirect stderr to avoid mixing with JSON-RPC output
        process = subprocess.run([command] + args, 
                               stdin=sys.stdin, 
                               stdout=sys.stdout, 
                               stderr=sys.stderr)
        return process.returncode
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"ERROR: Command not found: {command}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
