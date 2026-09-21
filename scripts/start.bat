@echo off
setlocal
cd /d %~dp0\..

echo [1/3] Checking Grafana volume...
docker volume inspect grafana-storage >nul 2>&1
if errorlevel 1 (
  echo Creating grafana-storage...
  docker volume create grafana-storage
  if errorlevel 1 exit /b 1
)

echo [2/3] Validating Compose config...
docker compose config >nul
if errorlevel 1 exit /b 1

echo [3/3] Starting stack...
docker compose up -d --build
if errorlevel 1 exit /b 1

echo.
docker compose ps

echo.
echo Stack started. vLLM may need additional time to load the model.
endlocal
