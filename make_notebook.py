"""Synchronize attention.ipynb with the percent-cell worksheet attention.py."""

import json
from pathlib import Path


def cell(kind, lines):
    source = "".join(lines).strip("\n")
    result = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


def main():
    source = Path("attention.py").read_text(encoding="utf-8")
    cells = []
    kind = None
    lines = []
    for line in source.splitlines(keepends=True):
        if line.startswith("# %%"):
            if kind is not None:
                cells.append(cell(kind, lines))
            kind = "markdown" if "[markdown]" in line else "code"
            lines = []
        elif kind == "markdown":
            lines.append(line[2:] if line.startswith("# ") else "\n" if line == "#\n" else line)
        elif kind == "code":
            lines.append(line)
    if kind is not None:
        cells.append(cell(kind, lines))

    notebook = {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    Path("attention.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
