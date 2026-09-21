from locust import HttpUser, task, constant


class VLLMUser(HttpUser):
    wait_time = constant(0)

    def on_start(self):
        # Avoid host proxy settings (for example Clash) interfering with local tests.
        self.client.trust_env = False

    @task
    def chat_completion(self):
        payload = {
            "model": "Qwen/Qwen3-0.6B",
            "messages": [
                {
                    "role": "user",
                    "content": "请详细解释大语言模型推理服务的工作流程。",
                }
            ],
            "max_tokens": 128,
            "min_tokens": 128,
            "ignore_eos": True,
            "stream": False,
            "chat_template_kwargs": {
                "enable_thinking": False,
            },
        }

        with self.client.post(
            "/v1/chat/completions",
            json=payload,
            name="/v1/chat/completions",
            timeout=300,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return

            try:
                data = response.json()
                if not data.get("choices"):
                    response.failure("Response does not contain choices")
                else:
                    response.success()
            except Exception as exc:
                response.failure(f"Invalid JSON response: {exc}")
