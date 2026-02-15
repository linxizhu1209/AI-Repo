"""REST API 진입점: 지시 수신 -> Agent 실행 """
from __future__ import annotations
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 프로젝트 루트 = web-agent
BASE_DIR = Path(__file__).resolve().parent.parent

class RunRequest(BaseModel):
    instruction: str
    spec: str = "specs/app.json"

class RunResponse(BaseModel):
    status: str
    project_name: str
    project_dir: str

app = FastAPI(title="web Agent API", version="0.1.0")

""" 자연어 지시를 받아 spec 수정 + 프로젝트 생성 수행 """
@app.post("/api/run", response_model=RunResponse)
def api_run(req: RunRequest):
    from agent.llm_parser import _call_ollama
    from agent.main import run_agent_full

    spec_path = BASE_DIR / req.spec
    if not spec_path.exists():
        raise HTTPException(status_code=400, detail=f"Spec not found: {req.spec}")

    instructions = _call_ollama(req.instruction)
    if not instructions:
        raise HTTPException(
            status_code=400,
            detail="Failed to convert natural language to instructions. Is Ollama running?: ollama run llama3.2"
        )

    try:
        project_dir = run_agent_full(spec_path, instructions)
        project_name = project_dir.name
        return RunResponse(
            status="ok",
            project_name=project_name,
            project_dir=str(project_dir),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health():
    return {"status": "ok"}