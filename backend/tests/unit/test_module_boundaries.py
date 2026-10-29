"""Keep domain ownership and SQL/HTTP direction enforceable (FR-SEC-11)."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_domain_layers_do_not_reach_back_into_http_or_execute_sql() -> None:
    violations = []
    for folder in ROOT.iterdir():
        if not folder.is_dir() or folder.name in [".venv", "tests", "__pycache__"]:
            continue
        for file in folder.rglob("*.py"):
            if ".venv" in file.parts:
                continue
            parts = file.relative_to(ROOT).with_suffix("").parts
            layer = next((name for name in ["urls", "views", "services", "repositories"] if name in parts), None)
            if layer is None:
                continue
            tree = ast.parse(file.read_text(encoding="utf8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    target = node.module.split(".")
                    if layer in ["services", "repositories"] and any(name in target for name in ["urls", "views"]):
                        violations.append(f"{file.name}:{node.lineno}: {layer} imports HTTP")
                    if node.module == "backend.core.database.connection" and layer != "repositories":
                        if any(name.name in ["fetch_all", "fetch_one", "fetch_value", "execute", "execute_returning"] for name in node.names):
                            violations.append(f"{file.name}:{node.lineno}: SQL outside repository")
                if layer != "repositories" and isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "db" and node.func.attr in ["fetch_all", "fetch_one", "fetch_value", "execute", "execute_returning"]:
                        violations.append(f"{file.name}:{node.lineno}: SQL outside repository")
    assert violations == []


def test_no_business_implementation_remains_in_global_layer_directories() -> None:
    for name in ["controllers", "services", "repositories"]:
        assert list((ROOT / name).glob("*.py")) == []
    for name in ["django", "medlive", "modules", "api", "workers"]:
        assert not (ROOT / name).exists()
    assert (ROOT / "core" / "settings.py").is_file()
    assert (ROOT / "queues" / "services" / "queue.py").is_file()
    assert not [p for p in ROOT.rglob("*") if p.suffix in [".ts", ".js", ".mjs"] and ".venv" not in p.parts]
