@echo off
setlocal
cd /d %~dp0\..
if "%~1"=="" (
  echo Usage: restart.bat SERVICE
  echo Example: restart.bat api
  exit /b 1
)
docker compose restart %~1
endlocal
