@echo off
setlocal
cd /d %~dp0\..
if "%~1"=="" (
  docker compose logs -f
) else (
  docker compose logs -f %~1
)
endlocal
