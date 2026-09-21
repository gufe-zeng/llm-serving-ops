# Troubleshooting Guide

本手册按“症状 -> 定位 -> 原因 -> 解决”组织。优先分层排查，不要一次重装所有组件。

## 1. Docker Desktop WSL engine failed to start

### Symptom

```text
starting WSL engine: installing main distribution: copying distribution: Access is denied
```

### Checklist

```cmd
wsl --version
wsl -l -v
docker version
```

### Verified resolution in this project

清理/重命名旧 Docker Desktop 状态后升级到新版本 Docker Desktop，重新建立 `docker-desktop` WSL distribution。不要在不确认数据需求时直接删除旧目录。

---

## 2. Docker Hub pull timeout / TLS handshake timeout

### Symptom

```text
timeout awaiting response headers
TLS handshake timeout
auth.docker.io/token ... timeout
```

### Cause

本机 Clash/代理与 Docker Desktop 网络路径不一致。

### Checks

```cmd
curl -I https://hub.docker.com
```

检查 Docker Desktop Proxy 设置。不要把镜像下载问题和容器运行时错误混为一谈。

---

## 3. GPU container cannot use CUDA

### Validation command

```cmd
docker run --rm -it --gpus=all nvcr.io/nvidia/k8s/cuda-sample:nbody nbody -gpu -benchmark
```

成功执行 CUDA 计算后，才能继续排查 vLLM；否则先修复 Windows -> WSL2 -> Docker -> GPU 链路。

---

## 4. vLLM says free GPU memory is insufficient

### Symptom

```text
free memory 3.21/4.0 GiB < desired 0.85 * 4.0 GiB
```

### Cause

`--gpu-memory-utilization 0.85` 要求的预算超过当前可用显存。

### Verified fix

```text
--gpu-memory-utilization 0.75
```

理解：该参数是 vLLM 的显存预算目标，不等于 `nvidia-smi` 中最终整卡显存占用百分比。

---

## 5. vLLM V2 runner: UVA is not available

### Symptom

```text
RuntimeError: UVA is not available
```

### Environment

WSL2 + GTX 1650 + vLLM 0.29.0。

### Verified workaround

```text
VLLM_USE_V2_MODEL_RUNNER=0
```

Compose 中：

```yaml
environment:
  VLLM_USE_V2_MODEL_RUNNER: "0"
```

该 workaround 与版本有关。升级 vLLM 后应重新验证。

---

## 6. Qwen only outputs `<think>` and stops

### Symptom

```json
"finish_reason": "length"
```

且输出主要是 `<think>...</think>`。

### Cause

Qwen3 thinking mode 消耗了有限的 `max_tokens`。

### Fix

请求中加入：

```json
"chat_template_kwargs": {
  "enable_thinking": false
}
```

---

## 7. Grafana localhost:3000 empty / refused, but container is Up

### Diagnostic split

容器内部：

```cmd
docker exec grafana wget -qO- http://127.0.0.1:3000/api/health
```

Windows 侧绕过代理：

```cmd
curl --noproxy "*" -v http://127.0.0.1:3000/api/health
```

### Verified issue

本机 Clash/localhost 路径干扰。`127.0.0.1:3000` 可正常访问。

### Rule

本项目文档统一优先使用 `127.0.0.1`。

---

## 8. Prometheus Target = DOWN

### Checks

1. vLLM 是否在线：

```cmd
curl http://127.0.0.1:8000/metrics
```

2. Compose 中 target 是否为 service name：

```yaml
- "vllm:8000"
```

3. Prometheus 配置是否被正确挂载：

```cmd
docker compose logs prometheus
```

4. 查询：

```promql
up{job="vllm"}
```

`1` 为 UP，`0` 为 DOWN。

---

## 9. Grafana panel一直是 0

不要先怀疑 Grafana。检查指标是否是瞬态、Prometheus scrape 是否错过。

例如 `scrape_interval: 5s`，而请求只持续 2~3 秒，则 Running/Waiting 可能在两次 scrape 之间完整发生。

解决思路：

- 使用更长请求；
- 制造持续并发；
- 必要时临时缩短 scrape interval；
- 直接查询 `/metrics` 区分“vLLM 没产生指标”还是“Prometheus 没采到”。

---

## 10. Nginx returns 502 Bad Gateway

### Meaning

Nginx 自己活着，但 upstream FastAPI 不可用。

### Checks

```cmd
curl http://127.0.0.1:8081/nginx-health
curl http://127.0.0.1:8080/health
docker compose logs nginx
docker compose logs api
```

如果 `/nginx-health` 正常，而 `/health` 经过 Nginx 返回 502，优先排查 FastAPI。

---

## 11. LLM request gets 504 / times out behind Nginx

LLM 请求可能包含 queue、prefill、decode，耗时远高于普通 Web API。

当前配置：

```nginx
proxy_connect_timeout 5s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;
```

`proxy_read_timeout` 太短会让模型仍在生成时网关先断开。

---

## 12. Docker Compose cannot find Dockerfile

### Symptom

```text
failed to read dockerfile: open Dockerfile: no such file or directory
```

### Checks

```cmd
dir /a E:\project\llm-serving-ops\api
```

常见原因：Windows 记事本保存成 `Dockerfile.txt`。

### Fix

```cmd
ren E:\project\llm-serving-ops\api\Dockerfile.txt Dockerfile
```

然后先单独验证：

```cmd
docker compose build api
```

---

## 13. Port already allocated

### Symptom

```text
Bind for 0.0.0.0:xxxx failed: port is already allocated
```

### Cause

旧的手工 `docker run` 容器或本机 Uvicorn 仍在监听同一端口。

### Checks

```cmd
docker ps
netstat -ano | findstr :8000
netstat -ano | findstr :8080
netstat -ano | findstr :8081
```

Compose 启动前停止旧服务。

---

## 14. Compose starts API before model is ready

`depends_on` 默认只保证 container start order，不保证 application readiness。

因此刚启动时：

```text
FastAPI Up
vLLM loading model
/health -> 503
```

并不一定是故障。等待 vLLM 完成模型加载后重试。

生产环境可以进一步加入 healthcheck + service_healthy；学习项目不必过度复杂化。

---

## Layered troubleshooting order

遇到问题时优先按以下顺序：

```text
1. Host / WSL / GPU
2. Docker container
3. vLLM model service
4. FastAPI
5. Nginx
6. Prometheus scrape
7. Grafana query
8. Locust client
```

每一层都用最小健康检查验证，不要直接从浏览器现象猜根因。
