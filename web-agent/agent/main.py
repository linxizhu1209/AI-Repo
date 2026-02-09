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
        "__BASE_PACKAGE_PATH__": base_package.replace(".", "/"),
    }
    replace_in_files(dest, replacements)
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


if __name__ == "__main__":
    main()
