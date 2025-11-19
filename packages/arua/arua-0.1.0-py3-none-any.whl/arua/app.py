"""FastAPI application for ARUA.

This module exposes the ASGI ``app`` for use by both the CLI runner
and the test suite.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .calculator import add, multiply

app = FastAPI(title="ARUA Demo API")


class MultiplyRequest(BaseModel):
    a: float
    b: float


@app.get("/", summary="Health check")
async def root() -> dict[str, Any]:
    return {"message": "ARUA is up"}


@app.get("/add", summary="Add two numbers")
async def add_endpoint(a: float, b: float) -> dict[str, Any]:
    try:
        result = add(a, b)
    except Exception as exc:  # pragma: no cover - trivial error path
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"result": result}


@app.post("/multiply", summary="Multiply two numbers")
async def multiply_endpoint(payload: MultiplyRequest) -> dict[str, Any]:
    try:
        result = multiply(payload.a, payload.b)
    except Exception as exc:  # pragma: no cover - trivial error path
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"result": result}
