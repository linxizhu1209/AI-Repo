""" 자연어 지시를 spec_editor 형식의 구조화된 지시로 변환. (Ollama/OpenAI)"""
from __future__ import annotations
import os
import re

SYSTEM_PROMPT = """
당신은 프로젝트 spec을 수정하는 에이전트입니다. 사용자 요청을 다음 형식의 지시문 리스트로 변환해주세요.
한줄에 하나의 지시만 출력합니다.

지원 형식: 
- (모듈명)에 (필드명) 필드 추가
- (모듈명)에 (필드명) 필드 (타입)으로 추가 (타입: String, Boolean, Integer, Long)
- (모듈명)에 (필드명) 필드 삭제
- (모듈명) 모듈 추가, 필드 (이름:타입, 이름:타입,...) 예: todo 모듈 추가, 필드 title:String, done:Boolean

모듈명과 필드명은 반드시 영문 소문자로만 출력하세요.
한글이 있으면 영문으로 번역해서 넣으세요. 예: 할일→todo, 담당자→assignee,
요청과 무관한 내용은 출력하지 마세요. 지시문만 출력합니다.
"""

USER_PROMPT_TEMPLATE = """다음 요청을 위 형식의 지시문으로 변환해주세요. 한 줄에 하나씩만 출력해주세요.
요청: {text}"""

""" 자연어 요청을 지시문 리스트로 변환 """
def _parse_instructions(content: str) -> list[str]:
    instructions = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue

        # 불릿/번호 제거: "- ", "* ", "1. ", "1) " 등
        line = re.sub(r"^(\-|\*|\•)\s+", "", line)
        line = re.sub(r"^\d+[\.\)]\s+", "", line)
        
        if line:
            instructions.append(line)
    return instructions

""" Ollama 로컬 모델 호출 """
def _call_ollama(text: str, model: str = "llama3.2") -> list[str]:
    try:
        from openai import OpenAI
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=text)}
            ],
            temperature=0.1,
        )
        content = (resp.choices[0].message.content or "").strip()
        return _parse_instructions(content)
    except Exception as e:
        print(f"[Ollama Error] {e}")
        print("  -> Ollama 실행 확인: ollama run llama3.2")
        return []
