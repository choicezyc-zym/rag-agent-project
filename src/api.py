import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
LOG_DIR = os.path.join(PROJECT_ROOT, "outputs")
API_LOG_PATH = os.path.join(LOG_DIR, "api_requests.jsonl")

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from multi_step_agent import run_multi_step_agent_with_history


app = FastAPI(
    title="Local RAG Agent API",
    description="A FastAPI backend for the local RAG + Multi-step AI Agent project.",
    version="1.1.0"
)


class AgentRequest(BaseModel):
    task: str = Field(..., description="User task for the Agent")
    max_steps: int = Field(5, ge=1, le=10, description="Maximum Agent execution steps")
    max_retries: int = Field(2, ge=0, le=5, description="Maximum retry attempts for invalid tool calls")


class AgentResponse(BaseModel):
    request_id: str
    final_answer: str
    history: List[Dict[str, Any]]
    meta: Dict[str, Any]


def write_api_log(record: Dict[str, Any]) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

    with open(API_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


@app.get("/")
def root():
    return {
        "message": "Local RAG Agent API is running.",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "rag_agent_api",
        "version": "1.1.0"
    }


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    if not request.task.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "request_id": request_id,
                "error": "Task cannot be empty."
            }
        )

    try:
        final_answer, history = run_multi_step_agent_with_history(
            user_goal=request.task,
            max_steps=request.max_steps,
            max_retries=request.max_retries
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        response_data = {
            "request_id": request_id,
            "final_answer": final_answer,
            "history": history,
            "meta": {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "max_steps": request.max_steps,
                "max_retries": request.max_retries,
                "step_count": len(history),
                "latency_ms": latency_ms,
                "status": "success"
            }
        }

        write_api_log({
            "request_id": request_id,
            "timestamp": response_data["meta"]["timestamp"],
            "task": request.task,
            "max_steps": request.max_steps,
            "max_retries": request.max_retries,
            "final_answer": final_answer,
            "history": history,
            "latency_ms": latency_ms,
            "status": "success",
            "error": None
        })

        return response_data

    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)

        write_api_log({
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "task": request.task,
            "max_steps": request.max_steps,
            "max_retries": request.max_retries,
            "final_answer": None,
            "history": [],
            "latency_ms": latency_ms,
            "status": "failed",
            "error": str(e)
        })

        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "error": "Agent execution failed.",
                "message": str(e)
            }
        )