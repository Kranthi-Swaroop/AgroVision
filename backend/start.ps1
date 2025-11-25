# Local development start script
Set-Location $PSScriptRoot
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
