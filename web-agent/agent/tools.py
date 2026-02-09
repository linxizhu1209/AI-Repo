from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def copy_template(template_dir: Path, dest_dir: Path) -> None:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    shutil.copytree(template_dir, dest_dir)

def replace_in_files(root: Path, replacements: dict[str, str], exts=(".java", ".yaml", ".html", ".properties", ".gradle", ".md")) -> None:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in exts:
            text = p.read_text(encoding="utf-8")
            for k, v in replacements.items():
                text = text.replace(k, v)
            p.write_text(text, encoding="utf-8")

""" 명령어 실행하고, 실패하면 예외 던지는 함수 """
def run_cmd(cmd: list[str], cwd: Path) -> None:
    print(f"\n[RUN] {' '.join(cmd)} (cwd={cwd})")

    if cmd and cmd[0].lower().endswith((".bat", ".cmd")):
        cmd = ["cmd", "/c", *cmd]

    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, shell=False)
    
    if proc.stdout:
        print(proc.stdout)
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")