"""Convert Google-style Args/Returns/Raises docstrings to Sphinx field lists."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "ovrl_sdk" / "client.py",
    ROOT / "ovrl_sdk" / "soroban.py",
    ROOT / "ovrl_sdk" / "config.py",
    ROOT / "ovrl_sdk" / "types.py",
    ROOT / "ovrl_sdk" / "constants.py",
    ROOT / "ovrl_sdk" / "exceptions.py",
    ROOT / "ovrl_sdk" / "__init__.py",
    ROOT / "main.py",
]


def convert_docstring(doc: str) -> str:
    text = inspect.cleandoc(doc)
    lines = text.splitlines()
    new_lines: List[str] = []
    params: List[List[str]] = []
    returns: List[str] = []
    yields: List[str] = []
    raises: List[List[str]] = []

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped in {"Args:", "Parameters:"}:
            while new_lines and not new_lines[-1].strip():
                new_lines.pop()
            i += 1
            current = None
            while i < len(lines) and lines[i].startswith("    "):
                entry = lines[i].strip()
                if not entry:
                    i += 1
                    continue
                if ":" in entry:
                    name, desc = entry.split(":", 1)
                    current = [name.strip(), desc.strip()]
                    params.append(current)
                elif current is not None:
                    current[1] += f" {entry}"
                i += 1
            continue
        if stripped == "Returns:":
            while new_lines and not new_lines[-1].strip():
                new_lines.pop()
            i += 1
            chunk: List[str] = []
            while i < len(lines) and lines[i].startswith("    "):
                entry = lines[i].strip()
                if entry:
                    chunk.append(entry)
                i += 1
            if chunk:
                returns.append(" ".join(chunk))
            continue
        if stripped == "Yields:":
            while new_lines and not new_lines[-1].strip():
                new_lines.pop()
            i += 1
            chunk = []
            while i < len(lines) and lines[i].startswith("    "):
                entry = lines[i].strip()
                if entry:
                    chunk.append(entry)
                i += 1
            if chunk:
                yields.append(" ".join(chunk))
            continue
        if stripped == "Raises:":
            while new_lines and not new_lines[-1].strip():
                new_lines.pop()
            i += 1
            current = None
            while i < len(lines) and lines[i].startswith("    "):
                entry = lines[i].strip()
                if not entry:
                    i += 1
                    continue
                if ":" in entry:
                    exc, desc = entry.split(":", 1)
                    current = [exc.strip(), desc.strip()]
                    raises.append(current)
                elif current is not None:
                    current[1] += f" {entry}"
                i += 1
            continue
        new_lines.append(lines[i])
        i += 1

    filtered: List[str] = []
    for line in new_lines:
        if line == "" and filtered and filtered[-1] == "":
            continue
        filtered.append(line)
    new_lines = filtered

    while new_lines and new_lines[-1] == "":
        new_lines.pop()

    if params or returns or raises or yields:
        if new_lines and new_lines[-1] != "":
            new_lines.append("")

    for name, desc in params:
        new_lines.append(f":param {name}: {desc}")
    for ret in returns:
        new_lines.append(f":returns: {ret}")
    for yval in yields:
        new_lines.append(f":yields: {yval}")
    for exc, desc in raises:
        new_lines.append(f":raises {exc}: {desc}")

    result = "\n".join(new_lines)
    return result


def rebuild_block(indent: str, text: str) -> List[str]:
    text = text.rstrip()
    lines = text.splitlines()
    if not lines:
        return [f'{indent}"""""']
    block: List[str] = []
    if len(lines) == 1:
        block.append(f'{indent}"""{lines[0]}"""')
        return block
    block.append(f'{indent}"""{lines[0]}')
    for line in lines[1:]:
        block.append(f"{indent}{line}")
    block.append(f'{indent}"""')
    return block


def transform_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    tree = ast.parse(text)
    replacements = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        first_stmt = getattr(node, "body", [])[:1]
        if not first_stmt:
            continue
        expr = first_stmt[0]
        if not isinstance(expr, ast.Expr):
            continue
        value = expr.value
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        markers = (
            "Args:",
            "Parameters:",
            "Returns:",
            "Raises:",
            "Yields:",
            ":param ",
            ":returns:",
            ":raises ",
            ":yields:",
        )
        if all(marker not in doc for marker in markers):
            continue
        start = value.lineno - 1
        end_lineno = getattr(value, "end_lineno", value.lineno)
        end = end_lineno - 1
        block_lines = lines[start : end + 1]
        indent_idx = block_lines[0].find('"""')
        indent = block_lines[0][: indent_idx if indent_idx >= 0 else 0]
        converted = convert_docstring(doc)
        if converted == doc:
            continue
        new_block = rebuild_block(indent, converted)
        replacements.append((start, end, new_block))

    if not replacements:
        return

    # Apply from bottom to top to keep indices valid
    for start, end, new_block in sorted(replacements, key=lambda item: item[0], reverse=True):
        lines[start : end + 1] = new_block

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    for target in TARGETS:
        if target.exists():
            transform_file(target)


if __name__ == "__main__":
    main()
