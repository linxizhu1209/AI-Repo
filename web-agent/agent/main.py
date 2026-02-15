from __future__ import annotations
import shutil
from pathlib import Path
from agent.tools import ensure_dir, copy_template, replace_in_files, run_cmd
import json
from agent.generator import generate_reservation_module, generate_home_page, ensure_app_css
from agent.spec_editor import apply_instruction
import argparse
from agent.runner import run_agent_instructions
from agent.llm_parser import _call_ollama


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "agent" / "templates" / "spring-thymeleaf"
OUTPUT_DIR = BASE_DIR / "generated"

def create_project(project_name: str, base_package: str) -> Path:
    ensure_dir(OUTPUT_DIR)
    dest = OUTPUT_DIR / project_name

    copy_template(TEMPLATE_DIR, dest)

    replacements = {
        "__PROJECT_NAME__" : project_name,
        "__BASE_PACKAGE__" : base_package,
    }
    replace_in_files(dest, replacements)
    
    replace_base_package_path(dest, base_package)    
    return dest


"""Gradle Wrapper(gradlew.bat)가 없으면 생성하는 함수"""
def ensure_gradle_wrapper(project_dir: Path) -> None:
    if (project_dir / "gradlew.bat").exists():
        return
    
    run_cmd(["gradle", "wrapper"], cwd=project_dir)

"""프로젝트 빌드/테스트 확인 함수
    Gradle Wrapper로 프로젝트 테스트
"""
def verify_project(project_dir: Path) -> None:
    run_cmd(["gradlew.bat", "test"], cwd=project_dir)


def main():
    # todo 자연어 입력을 spec 으로 변경
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="specs/reservation.json")
    # -i "지시1" -i "지시2" 이런식으로 리스트에 여러 지시가 들어갈 수 있음
    parser.add_argument("--instruction", "-i", action="append",default=None, metavar="TEXT",help="지시문(여러 번 가능) (예: -i 'reservation에 phone 필드 삭제' -i 'reservation에 phon 필드 추가')")
    parser.add_argument("--natural", "-n", default=None, metavar="TEXT", help="자연어 지시 (Ollama/LLM으로 구조화된 지시로 변환 후 적용)")

    args = parser.parse_args()

    spec_path = BASE_DIR / args.spec
    instructions = list(args.instruction or [])

    # 자연어 지시가 있으면 LLM(Ollama)으로 변환 후 instructions에 추가
    if args.natural:
        nl_instructions = _call_ollama(args.natural)
        if nl_instructions:
            instructions.extend(nl_instructions)
            print(f"[LLM] 자연어 -> {len(nl_instructions)}개 지시로 변환됨")
        else:
            print(f"[Warn] 자연어 변환 실패. Ollama: ollama run llama3.2")

    if getattr(args, "instruction_file", None):
        path = BASE_DIR / args.instruction_file
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    instructions.append(line)
        else:
            print(f"[Warn] instruction file not found: {path}")
    
    spec = run_agent_instructions(spec_path, instructions)
    if instructions:
        print(f"[Spec updated] {len(instructions)} instruction(s) applied")
    
    project_name = spec["projectName"]
    base_package = spec["basePackage"]

    project_dir = create_project(project_name, base_package)
    
    # 공통 CSS 생성
    ensure_app_css(project_dir)

    # module 생성
    modules = spec.get("modules")
    if modules:
        for m in modules:
            generate_reservation_module(project_dir, base_package, m)
        # 홈 페이지 생성
        generate_home_page(project_dir, base_package, modules)
    else:
        generate_reservation_module(project_dir, base_package, spec["module"])
        # 단일 모듈도 홈 페이지 생성
        generate_home_page(project_dir, base_package, [spec["module"]])

    verify_project(project_dir)
    print("\n Tests passed! Next: run the server with:")
    print(f"   cd {project_dir}")
    print("    gradlew.bat bootRun")

def replace_base_package_path(project_dir: Path, base_package: str) -> None:
    """__BASE_PACKAGE_PATH__디렉토리를 실제 패키지 경로로 변경"""
    src_java = project_dir / "src" / "main" / "java"
    placeholder = src_java / "__BASE_PACKAGE_PATH__"
    if not placeholder.exists():
        return

    target = src_java / Path(*base_package.split("."))
    
    # target이 없으면 rename
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        placeholder.rename(target)
        return
    
    # target이 이미 있으면 placeholder내부를 target으로 "merge"
    for item in placeholder.rglob("*"):
        rel = item.relative_to(placeholder)
        dest = target / rel
        if item.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(dest))
    
    shutil.rmtree(placeholder)

if __name__ == "__main__":
    main()
