import os
from pathlib import Path
from dotenv import load_dotenv

# Try to find .env in current directory or parent directory
env_paths = [
    Path.cwd() / ".env",
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env"
]

for path in env_paths:
    if path.exists():
        load_dotenv(dotenv_path=path)
        break

# Get the token from environment variables
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "PASTE_YOUR_TOKEN_HERE")
