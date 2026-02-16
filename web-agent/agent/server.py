"""REST API 진입점: 지시 수신 -> Agent 실행 """
from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
import os
import json
import httpx
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from dotenv import load_dotenv

load_dotenv()

DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
DISCORD_APP_ID = os.getenv("DISCORD_APP_ID")

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
    try:
        return run_agent_from_instruction(req.instruction, req.spec)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""서버 헬스 체크"""
@app.get("/api/health")
def health():
    return {"status": "ok"}

""" instruction + spec 으로 Agent 실행. /api/run 과 from-message/webhook 에서 사용"""
def run_agent_from_instruction(instruction: str, spec: str= "specs/app.json") -> RunResponse:
    from agent.llm_parser import _call_ollama
    from agent.main import run_agent_full

    spec_path = BASE_DIR / spec
    if not spec_path.exists():
        raise HTTPException(status_code=400, detail=f"Spec not found: {spec}")
    
    instructions = _call_ollama(instruction)

    print("[NL]", instruction)
    print("[INSTRUCTIONS]", instructions)

    if not instructions:
        raise HTTPException(
            status_code=400,
            detail="Failed to convert natural language to instructions. Is Ollama running?: ollama run llama3.2",
        )
    
    project_dir = run_agent_full(spec_path, instructions)
    return RunResponse(
        status="ok",
        project_name=project_dir.name,
        project_dir=str(project_dir),
    )

""" discord 요청인지 확인 """
def verify_discord_signature(request: Request, raw_body: bytes):
    sig = request.headers.get("X-Signature-Ed25519")
    ts = request.headers.get("X-Signature-Timestamp")
    if not sig or not ts:
        raise HTTPException(status_code=401, detail="Missing Discord signature headers")
    
    try:
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(ts.encode() + raw_body, bytes.fromhex(sig))
    except BadSignatureError:
        raise HTTPException(status_code=401, detail="Invalid Discord signature")

""" 결과를 Discord에 다시 보내는 함수 (비동기) """
async def send_followup(interaction_token: str, content: str):
    # Follow-up message endpoint
    url = f"https://discord.com/api/v10/webhooks/{DISCORD_APP_ID}/{interaction_token}"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json={"content": content})

"""시간이 오래걸리는 작업을 수행하고 결과메시지를 만드는 함수"""
def run_agent_and_notify(instruction: str, interaction_token: str):
    try:
        result = run_agent_from_instruction(instruction, "specs/app.json")
        # result는 Pydantic 모델이면 dict으로 변환
        msg = f"✅ 완료!\n- project: {result.project_name}\n- dir: {result.project_dir}"
    except Exception as e:
        msg = f"❌ 실패: {e}"
    # background task는 sync라서 httpx async를 직접 못 쓰니 간단히 동기 호출로 바꿔도 됨
    # 여기서는 가장 단순하게 새 이벤트루프 대신, httpx sync로 처리:
    import httpx as _httpx
    url = f"https://discord.com/api/v10/webhooks/{DISCORD_APP_ID}/{interaction_token}"
    _httpx.post(url, json={"content": msg}, timeout=10)

""" Discord 호출 엔드포인트"""
@app.post("/discord/interactions")
async def discord_interactions(request: Request, background: BackgroundTasks):
    raw = await request.body()
    verify_discord_signature(request, raw)
    payload = json.loads(raw.decode("utf-8"))

    # Discord가 endpoint 검증할 때 보내는 PING
    if payload.get("type") == 1:
        return {"type": 1}

    # Slash command 호출
    if payload.get("type") == 2:
        data = payload.get("data", {})
        options = data.get("options", [])

        instruction = None
        for opt in options:
            if opt.get("name") == "instruction":
                instruction = opt.get("value")
                break

        if not instruction:
            return {
                "type": 4,
                "data": {"content": "instruction 값이 없어. 예: /run instruction: ...", "flags": 64}
            }

        interaction_token = payload.get("token")

        # 3초 내 응답 필수 → 즉시 ACK(에페메랄)
        background.add_task(run_agent_and_notify, instruction, interaction_token)

        return {
            "type": 4,
            "data": {"content": "✅ 지시 받았어! 실행 시작할게.", "flags": 64}
        }

    return {"type": 4, "data": {"content": "지원하지 않는 이벤트 타입이야.", "flags": 64}}