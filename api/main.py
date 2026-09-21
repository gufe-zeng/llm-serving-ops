import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


VLLM_BASE_URL = os.getenv(
    "VLLM_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "Qwen/Qwen3-0.6B",
)

app = FastAPI(
    title="LLM Serving API",
    version="0.1.0",
    description="FastAPI gateway for a vLLM inference service.",
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    max_tokens: int = Field(default=128, ge=1, le=512)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


@app.get("/")
async def root():
    return {
        "service": "llm-serving-api",
        "status": "running",
    }


@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3.0, trust_env=False) as client:
            response = await client.get(f"{VLLM_BASE_URL}/v1/models")
            response.raise_for_status()

        return {
            "status": "ok",
            "vllm": "up",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "degraded",
                "vllm": "down",
                "error": str(exc),
            },
        )


@app.get("/model/info")
async def model_info():
    try:
        async with httpx.AsyncClient(timeout=5.0, trust_env=False) as client:
            response = await client.get(f"{VLLM_BASE_URL}/v1/models")
            response.raise_for_status()

        data = response.json()
        return {
            "configured_model": MODEL_NAME,
            "models": data.get("data", []),
        }
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Cannot connect to vLLM: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"vLLM returned HTTP {exc.response.status_code}",
        )


@app.post("/chat")
async def chat(request: ChatRequest):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": request.message,
            }
        ],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "stream": False,
        "chat_template_kwargs": {
            "enable_thinking": False,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=300.0, trust_env=False) as client:
            response = await client.post(
                f"{VLLM_BASE_URL}/v1/chat/completions",
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        return {
            "model": data.get("model", MODEL_NAME),
            "content": content,
            "usage": data.get("usage", {}),
        }
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Cannot connect to vLLM: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "vLLM request failed",
                "status_code": exc.response.status_code,
                "response": exc.response.text[:500],
            },
        )
    except (KeyError, IndexError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unexpected vLLM response format: {exc}",
        )
