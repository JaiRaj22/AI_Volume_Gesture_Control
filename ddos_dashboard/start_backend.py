import uvicorn
import os
import sys

if __name__ == "__main__":
    # Add the backend directory to the python path
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.append(backend_dir)

    print(f"Starting DDoS Dashboard Backend from {backend_dir}...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, app_dir=backend_dir)
