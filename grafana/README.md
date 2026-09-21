# Grafana Dashboard

项目使用外部 Docker volume `grafana-storage` 持久化 Grafana 配置和手工创建的 Dashboard。

核心面板：

1. Running Requests
2. Waiting Requests
3. KV Cache Usage
4. Generation Throughput
5. P95 Queue Time
6. P95 TTFT
7. P95 E2E Latency

如需把 Dashboard 纳入 Git 管理，可在 Grafana UI 中导出 JSON 后放入本目录。
