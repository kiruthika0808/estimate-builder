@echo off
title UniqNextGen Estimate Builder
cd /d "%~dp0"
echo Starting UniqNextGen Estimate Builder at http://localhost:8080
echo Keep this window open while you use the app. Close it to stop the server.
start "" http://localhost:8080
python -m http.server 8080 --bind 127.0.0.1
pause
