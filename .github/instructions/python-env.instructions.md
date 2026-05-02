---
description: "Use when running Python commands, installing packages, setting up the environment, writing pip or conda instructions, or running uvicorn/pytest/any Python tool for this project."
applyTo: "**/*.py"
---
# Python Environment

Always use the **conda environment `sys`** for all Python operations in this project.

- Activate before running anything: `conda activate sys`
- Install packages into it: `conda run -n sys pip install <pkg>` or activate first, then `pip install`
- Run the server: `conda run -n sys uvicorn gateway.main:app --reload --port 8000`
- Run tests: `conda run -n sys pytest`
- Never suggest using the base conda environment or a venv for this project
