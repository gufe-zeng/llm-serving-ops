# LLM Serving / LLMOps Interview Guide

建议回答方式：先讲“概念”，再讲“在这个项目里怎么做”，最后讲“遇到过什么问题”。不要只背定义。

## 1. vLLM 是什么？为什么不用直接 Transformers generate？

vLLM 是面向在线推理的 serving engine，核心关注高效调度、KV Cache 管理、batching 和 OpenAI-Compatible Server。Transformers `generate()` 更适合单进程实验或简单推理；在线服务还需要并发调度、请求队列、监控和稳定 API。

## 2. 你的完整请求链是什么？

```text
Client -> Nginx -> FastAPI -> vLLM -> Qwen -> vLLM -> FastAPI -> Nginx -> Client
```

同时 vLLM `/metrics` 被 Prometheus scrape，再由 Grafana 查询展示。

## 3. 为什么已经有 vLLM API，还要 FastAPI？

职责分层。vLLM 专注 GPU inference、scheduler、batching、KV Cache；FastAPI 负责业务参数校验、统一接口、异常处理，并为鉴权、日志、RAG、模型路由等扩展提供位置。

## 4. 为什么再加 Nginx？

统一入口、reverse proxy、upstream 解耦、forwarded headers、timeout 管理。真实 LLM 请求可能很长，网关必须正确配置 read timeout。

## 5. Reverse Proxy 是什么？

客户端只访问 Nginx，Nginx 再代表客户端访问后端 FastAPI。客户端不需要知道后端真实地址。

## 6. 502 和 504 有什么区别？

- 502：网关访问 upstream 失败或 upstream 返回异常协议响应；项目里 FastAPI 停掉后 Nginx `/health` 会出现典型 502。
- 504：upstream 连接建立后，网关等待响应超时；LLM 长推理时 `proxy_read_timeout` 太短容易触发。

## 7. TTFT 是什么？

Time To First Token，从请求到达直到第一个输出 token 出现的时间。它包含排队和 prefill 等前置开销，直接影响用户“多久开始看到回答”。

## 8. TTFT 和 E2E latency 的区别？

TTFT 关注开始回答的速度；E2E 关注整个回答完成的时间。通常 E2E >= TTFT，但不能把两个 P95 简单相减来推导 decode P95。

## 9. Queue Time 是什么？

请求到达 vLLM 后，在 scheduler WAITING 队列中等待被调度的时间。并发超过当前服务处理能力时 Waiting Requests 和 Queue Time 会升高。

## 10. 为什么 Throughput 稳定但 TTFT 变差？

服务可能已经达到 token generation capacity。GPU 仍持续以稳定 token/s 工作，但新请求不断排队，因此 Queue Time 和 TTFT 上升。吞吐好不代表用户延迟好。

## 11. KV Cache 是什么？

自回归 decode 时缓存历史 token 的 Key/Value，避免每生成一个新 token 都重新计算完整上下文。上下文越长、同时 active 的请求越多，KV Cache 压力越大。

## 12. KV Cache Usage = GPU Memory Usage 吗？

不是。`kv_cache_usage_perc` 表示 vLLM 分配给 KV Cache 的 blocks 使用比例；`nvidia-smi` 的显存还包含模型权重、CUDA runtime、workspace 等。

## 13. Gauge / Counter / Histogram 的区别？

- Gauge：瞬时状态，可增可减，如 running requests、waiting requests、KV cache usage。
- Counter：累计单调增长，如 generation tokens total；通常用 `rate()` 看单位时间增长。
- Histogram：对观测值分桶，如 TTFT/E2E；通常用 `histogram_quantile()` 算 P95/P99。

## 14. 为什么 generation_tokens_total 不能直接当吞吐？

它是累计 Counter。吞吐需要看单位时间变化，因此使用：

```promql
sum(rate(vllm:generation_tokens_total[1m]))
```

## 15. P95 是什么？

95% 的观测值不超过该分位点。P95 不是平均值。对 latency 使用 P95/P99 能更好反映尾延迟。

## 16. 为什么 `sum by (le)`？

Histogram quantile 必须保留 bucket 上界标签 `le`。聚合实例时可以合并其他标签，但不能丢掉 `le`。

## 17. Prometheus 是 Push 还是 Pull？

本项目是 Pull。Prometheus 按 `scrape_interval` 主动请求 vLLM `/metrics`，保存为 time series。

## 18. Grafana 直接监控 vLLM 吗？

不是。Grafana 查询 Prometheus；Prometheus 才负责 scrape vLLM 指标。完整链路：`vLLM -> Prometheus -> Grafana`。

## 19. 为什么 Grafana 有时看不到短请求的 Running/Waiting 峰值？

Prometheus 是离散采样。如果 scrape interval 5 秒，而请求只持续 2 秒，峰值可能完整发生在两次 scrape 之间。先直接查 `/metrics` 区分服务端是否产生指标，再判断是否采样遗漏。

## 20. Locust 的用户数等于 RPS 吗？

不等于。用户数控制并发虚拟用户。每个用户完成一个请求后何时发送下一个由 wait_time 和响应时间共同决定。RPS 是实际完成/发送请求速率。

## 21. Locust P95 与 vLLM TTFT 是同一个指标吗？

不是。当前 `stream=false` 时 Locust response time 近似客户端 E2E；TTFT 是服务端首 token 延迟。

## 22. Docker Compose 解决了什么问题？

把多个容器的镜像、端口、volume、环境变量、依赖关系、网络统一声明为配置，实现 `docker compose up -d` 一键拉起和统一生命周期管理。

## 23. Compose 中为什么用 `vllm:8000` 而不是容器 IP？

Compose 默认网络提供 DNS，service name 可稳定解析。容器 IP 会变化，不适合作为服务发现方式。

## 24. `depends_on` 是否保证 vLLM 模型已经 ready？

默认不保证，只保证 container 启动顺序。模型加载可能仍需时间，所以 API 刚启动时 `/health` 返回 503 是可能的。生产环境可增加 healthcheck + `service_healthy`。

## 25. 为什么 Docker Compose 不需要激活 Python `.venv`？

因为 FastAPI 依赖已经在 Docker image 中安装。`.venv` 只在 Windows 本机直接运行 Uvicorn/Locust 时需要。

## 26. 你遇到过哪些真实问题？

可回答四个：

1. 4GB 显存下 `gpu-memory-utilization=0.85` 预算过高，调整为 0.75。
2. WSL2 + vLLM V2 runner 报 `UVA is not available`，使用 V1 runner workaround。
3. Clash 影响 `localhost`，通过容器内 health check 与 `curl --noproxy "*" 127.0.0.1` 分层定位。
4. Compose build 找不到 Dockerfile，最终发现 Windows 文件扩展名问题。

## 27. 你如何排查一个 LLM API 不通的问题？

按层验证：GPU/WSL -> Docker -> vLLM `/v1/models` -> FastAPI `/health` -> Nginx `/nginx-health` 和代理 `/health` -> Prometheus target -> Grafana。每层只做最小健康检查，不直接猜。

## 28. 为什么 GTX 1650 也适合学习这个项目？

它不是生产性能平台，但足以学习完整 serving 链：GPU 容器、模型加载、显存约束、API、监控、排队和压测。4GB 显存反而能更直观看到资源约束。

## 29. 项目目前的边界是什么？

单机、单模型、学习型部署，没有 Kubernetes、多实例高可用、自动扩缩容、TLS、鉴权、生产级日志链路。面试时主动说清边界比夸大更可信。

## 30. 下一步如果继续扩展，你会做什么？

按岗位选择：

- LLMOps/AI Infra：Kubernetes、GPU scheduling、model autoscaling、OpenTelemetry、日志链路。
- LLM App：RAG、鉴权、多模型路由、缓存。
- 推理优化：continuous batching、quantization、不同 max-num-seqs / context length 性能对比。
