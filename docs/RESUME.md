# Resume Packaging

## Project name

**LLM Serving Ops - 大模型推理部署与可观测性平台**

## Recommended resume description

> 基于 Docker/WSL2 搭建 Qwen3-0.6B + vLLM 推理服务，封装 FastAPI 业务网关并通过 Nginx 提供统一反向代理；使用 Prometheus/Grafana 构建 LLM Serving 可观测性面板，监控 Running/Waiting Requests、KV Cache、Generation Throughput、P95 Queue Time、TTFT 与 E2E Latency；使用 Locust 完成多并发压测并分析吞吐与排队延迟关系，最终使用 Docker Compose 实现 vLLM、API、Nginx、Prometheus、Grafana 多服务一键编排。

建议拆成 3~4 条 bullet：

- 在 Windows + WSL2 + Docker Desktop 环境中部署 **Qwen3-0.6B + vLLM** OpenAI-Compatible 推理服务，完成 GPU 容器链路验证、显存预算配置及 WSL2 下 UVA 兼容问题定位。
- 使用 **FastAPI + Nginx** 构建推理业务入口，实现健康检查、模型信息、Chat API、反向代理、长请求超时与 upstream 解耦。
- 使用 **Prometheus + Grafana** 构建 LLM Serving Dashboard，监控请求队列、KV Cache、生成吞吐、P95 Queue Time、TTFT、E2E Latency，并掌握 Gauge/Counter/Histogram 对应 PromQL。
- 使用 **Locust** 完成并发压测，结合客户端 E2E 与服务端指标分析“吞吐稳定但排队导致 TTFT/E2E 上升”的饱和现象；通过 **Docker Compose** 实现 5 个核心服务统一编排和一键启动。

## Do not overclaim

当前项目不建议写：

- “支持大规模生产集群”
- “高可用多机部署”
- “Kubernetes 生产落地”
- “吞吐提升 xx%”——除非后续真的做参数调优并保存可复现结果
- “支持多模型自动弹性伸缩”

## 30-second interview intro

> 这个项目主要是补齐我在大模型推理部署和 LLMOps 上的工程能力。我从 Qwen3-0.6B 和 vLLM 开始，在 WSL2 + Docker 环境完成 GPU 推理服务部署，然后用 Prometheus/Grafana 监控请求队列、KV Cache、TTFT 和吞吐，用 Locust 做并发压测。之后增加 FastAPI 业务层和 Nginx 反向代理，最后用 Docker Compose 把 vLLM、API、Nginx、Prometheus、Grafana 统一编排。过程中实际遇到过显存预算不足、vLLM V2 runner 的 UVA 兼容问题、Clash 导致 localhost 访问异常以及 Compose Dockerfile 路径问题，我都是按服务层级逐步定位解决的。

## 2-minute technical intro

> 我把项目分成五层。第一层是模型推理层，用 vLLM 加载 Qwen3-0.6B，通过 OpenAI-Compatible API 提供推理；第二层是业务层，用 FastAPI 把 `/health`、`/model/info`、`/chat` 统一封装，避免业务直接依赖 vLLM 接口；第三层是入口层，用 Nginx 做 reverse proxy、upstream 和长请求 timeout；第四层是可观测性，通过 vLLM `/metrics` 接 Prometheus，再用 Grafana 展示 Running/Waiting、KV Cache、tokens/s、Queue Time、TTFT 和 E2E；第五层是压测和编排，用 Locust 做并发测试，用 Docker Compose 统一管理 5 个服务。这个项目最有价值的不是组件数量，而是我能解释请求从 Nginx 到 FastAPI、vLLM，再到 GPU 的完整链路，也能从 Waiting、Queue Time 和 TTFT 判断服务为什么变慢。
