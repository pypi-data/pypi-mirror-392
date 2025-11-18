"""Deepbrief package initialization."""

import argparse
import os

from dotenv import load_dotenv

from .app import app

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="Deepbrief Workflow API")
    parser.add_argument("--port", type=int, help="Port to listen on")
    parser.add_argument("--host", help="Host to bind to")
    args = parser.parse_args()

    port = args.port or int(os.getenv("DEEPBRIEF_PORT", "8080"))
    host = args.host or os.getenv("DEEPBRIEF_HOST", "0.0.0.0")
    import uvicorn
    uvicorn.run(app, host=host, port=port)
