import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token from environment variables
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "PASTE_YOUR_TOKEN_HERE")
