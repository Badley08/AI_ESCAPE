import os
import sys

# Auto-activation de l'environnement virtuel (.venv)
def _ensure_venv():
    if os.environ.get("_VENV_SEEN"):
        return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = script_dir
    venv_python = None

    for _ in range(5):
        for venv_name in [".venv", "env", "venv"]:
            if sys.platform == "win32":
                candidate = os.path.join(current_dir, venv_name, "Scripts", "python.exe")
            else:
                candidate = os.path.join(current_dir, venv_name, "bin", "python")
            if os.path.isfile(candidate):
                venv_python = candidate
                break
        if venv_python:
            break
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent

    if venv_python and os.path.realpath(sys.executable) != os.path.realpath(venv_python):
        os.environ["_VENV_SEEN"] = "1"
        os.execv(venv_python, [venv_python] + sys.argv)

_ensure_venv()

# Lancer le jeu principal depuis AI_ESCAPE/src/main.py ou src/main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
target_main = os.path.join(BASE_DIR, "AI_ESCAPE", "src", "main.py")
if not os.path.exists(target_main):
    target_main = os.path.join(BASE_DIR, "src", "main.py")

with open(target_main, "r", encoding="utf-8") as f:
    code = f.read()

sys.argv[0] = target_main
exec(compile(code, target_main, "exec"), {"__file__": target_main, "__name__": "__main__"})
