#!/bin/bash
cd "$(dirname "$0")"

uv run --python 3.11 uvicorn main:app --host 0.0.0.0 --port 5000
