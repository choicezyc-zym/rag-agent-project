import os
import sys
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from multi_step_agent import run_multi_step_agent_with_history


app = FastAPI(
    title="Local RAG Agent API",
    description="A FastAPI backend for the local RAG + Multi-step AI Agent project.",
    version="1.0.0"
)


class AgentRequest(BaseModel):
    task: str = Field(..., description="User task for the Agent")
    max_steps: int = Field(5, ge=1, le=10, description="Maximum Agent execution steps")
    max_retries: int = Field(2, ge=0, le=5, description="Maximum retry attempts for invalid tool calls")


class AgentResponse(BaseModel):
    final_answer: str
    history: List[Dict[str, Any]]
    meta: Dict[str, Any]


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
        "service": "rag_agent_api"
    }


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty.")

    try:
        final_answer, history = run_multi_step_agent_with_history(
            user_goal=request.task,
            max_steps=request.max_steps,
            max_retries=request.max_retries
        )

        return {
            "final_answer": final_answer,
            "history": history,
            "meta": {
                "max_steps": request.max_steps,
                "max_retries": request.max_retries,
                "step_count": len(history)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {e}")