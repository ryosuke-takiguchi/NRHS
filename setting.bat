echo off

python -m venv .venv
call .venv\scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt