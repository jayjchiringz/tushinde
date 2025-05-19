#!/usr/bin/env bash
# start.sh — Render startup script
uvicorn app.main:app --host 0.0.0.0 --port 10000
