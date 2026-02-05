#!/bin/bash
# SmartPaper Wrapper for Zotero
PROJECT_DIR="/Users/m99/Documents/SmartPaper"
cd "$PROJECT_DIR" || exit 1

PYTHON_BIN="./.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

SCRIPT_PATH="./cli_get_prompt_mode_paper.py"

# Run the script with passed arguments
"$PYTHON_BIN" "$SCRIPT_PATH" "$@"
