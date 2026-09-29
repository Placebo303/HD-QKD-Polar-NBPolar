import ast
import sys
from pathlib import Path

path = Path(__file__).resolve().parent / "run.py"
tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
found = []
for node in ast.walk(tree):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        found.append(node.lineno)
print(f"percent-format BinOp(Mod) expressions found: {len(found)} lines={found}")
sys.exit(0 if not found else 1)
