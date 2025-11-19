"""Module entrypoint to run `arua` app with Python -m arua."""

from __future__ import annotations

import uvicorn

from .app import app


def main() -> None:
    """Run the FastAPI app with uvicorn."""
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
