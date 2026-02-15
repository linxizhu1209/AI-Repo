"""Agent 실행 코어: 지시(spec 경로 + 지시 목록) -> 프로젝트 생성. """
from __future__ import annotations
from pathlib import Path
import json

from agent.tools import ensure_dir, copy_template, replace_in_files, run_cmd
from agent.generator import generate_reservation_module, generate_home_page, ensure_app_css
from agent.spec_editor import apply_instruction

""" spec 파일을 로드하고, 지시를 순서대로 적용한 뒤 수정된 spec 반환.
    지시가 하나라도 있으면 spec 파일을 덮어씀
    return : 수정된 spec dict (projectName, basePackage, module/modules)
"""
def run_agent_instructions(spec_path: Path, instructions: list[str]) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    for instr in instructions:
        spec = apply_instruction(spec, instr)
    if instructions:
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=0), encoding="utf-8")
    return spec
