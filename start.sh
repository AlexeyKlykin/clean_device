#!/bin/bash

/app/.venv/bin/python fill_in_the_table.py &
/root/.local/bin/uv run main.py
