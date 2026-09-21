# Learning Checklist

完成一项后打勾。目标不是背命令，而是能解释“为什么”。

## 1. GPU / Docker

- [ ] 能解释 Windows -> WSL2 -> Docker -> GPU 链路。
- [ ] 会用 `nvidia-smi`。
- [ ] 会用 CUDA sample 验证容器 GPU。
- [ ] 知道 Docker Desktop WSL backend 的作用。

## 2. vLLM

- [ ] 能启动 Qwen3-0.6B。
- [ ] 会测试 `/v1/models` 和 `/v1/chat/completions`。
- [ ] 能解释 `dtype`、`max-model-len`、`max-num-seqs`、`gpu-memory-utilization`。
- [ ] 能解释本机为什么需要 V1 runner workaround。
- [ ] 能解释 Qwen thinking mode 为什么会吃掉 `max_tokens`。

## 3. Observability

- [ ] 能解释 `vLLM -> Prometheus -> Grafana`。
- [ ] 会看 Running / Waiting / KV Cache。
- [ ] 会用 `rate()` 算 tokens/s。
- [ ] 会用 `histogram_quantile()` 算 P95。
- [ ] 能区别 Queue Time / TTFT / E2E。

## 4. Load test

- [ ] 能解释 Locust Users 与 RPS 不等价。
- [ ] 能区别客户端 E2E 与服务端 TTFT。
- [ ] 能解释“吞吐稳定但 TTFT 上升”的排队现象。

## 5. FastAPI / Nginx

- [ ] 能解释为什么 vLLM 前还需要 FastAPI。
- [ ] 能解释 Reverse Proxy、Upstream、Timeout。
- [ ] 能区别 502 与 504。
- [ ] 会用 `/health` 做分层排障。

## 6. Docker Compose

- [ ] 能解释 Compose service name DNS。
- [ ] 知道 `depends_on` 不等于应用 ready。
- [ ] 会 `config / up / ps / logs / restart / down`。
- [ ] 知道 Compose 不需要激活 `.venv`。

## 7. 求职表达

- [ ] 30 秒能讲清项目。
- [ ] 2 分钟能讲清 5 层架构。
- [ ] 至少能详细讲 2 个真实故障及定位过程。
- [ ] 不夸大为 Kubernetes/高可用/生产集群。
