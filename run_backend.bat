@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting Plant Disease Detection / BharatCrop AI Backend
echo URL: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo ========================================================
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
