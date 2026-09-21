@echo off
setlocal

echo === vLLM models ===
curl --noproxy "*" -s http://127.0.0.1:8000/v1/models
echo.
echo.

echo === FastAPI health ===
curl --noproxy "*" -s http://127.0.0.1:8080/health
echo.
echo.

echo === Nginx health ===
curl --noproxy "*" -s http://127.0.0.1:8081/nginx-health
echo.
echo.

echo === Nginx -> FastAPI -> vLLM model info ===
curl --noproxy "*" -s http://127.0.0.1:8081/model/info
echo.
echo.

echo === Prometheus health ===
curl --noproxy "*" -s http://127.0.0.1:9090/-/healthy
echo.
echo.

echo === Grafana health ===
curl --noproxy "*" -s http://127.0.0.1:3000/api/health
echo.
echo.

echo Smoke test finished. Review each response above.
endlocal
