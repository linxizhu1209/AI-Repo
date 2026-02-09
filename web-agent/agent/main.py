from __future__ import annotations
from pathlib import Path
from agent.tools import ensure_dir, copy_template, replace_in_files, run_cmd

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
    project_name = "demo-service"
    base_package = "com.example.demoservice"

    project_dir = create_project(project_name, base_package)
    print(f"\n Project generated at: {project_dir}")
    
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
    target.parent.mkdir(parents=True, exist_ok=True)
    placeholder.rename(target)

if __name__ == "__main__":
    main()
