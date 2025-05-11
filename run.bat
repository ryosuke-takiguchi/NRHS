@echo off
cd /d %~dp0
call .venv\scripts\activate
python scripts\run_allocation.py