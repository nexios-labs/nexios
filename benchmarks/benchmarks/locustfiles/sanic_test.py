from locust import HttpUser, between, task


class RoundRobinUser(HttpUser):
    wait_time = between(0.1, 0.1)  # Minimal delay
    host = "http://127.0.0.1:8002"
    endpoints = ["/", "/json", "/echo", "/delay/0.1"]
    current = 0

    @task
    def cycle_endpoints(self):
        endpoint = self.endpoints[self.current]
        if endpoint == "/echo":
            payload = {
                "message": "Hello World",
                "number": 42,
                "boolean": True,
                "array": [1, 2, 3],
                "object": {"key": "value"},
            }
            self.client.post(endpoint, json=payload)
        else:
            self.client.get(endpoint)
        self.current = (self.current + 1) % len(self.endpoints)
