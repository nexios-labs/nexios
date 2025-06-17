from locust import HttpUser, between, task


class NexiosUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://127.0.0.1:8005"

    @task(1)
    def get_root(self):
        self.client.get("/")

    @task(1)
    def get_json(self):
        self.client.get("/json")

    @task(1)
    def post_echo(self):
        payload = {
            "message": "Hello World",
            "number": 42,
            "boolean": True,
            "array": [1, 2, 3],
            "object": {"key": "value"},
        }
        self.client.post("/echo", json=payload)

    @task(1)
    def get_delay(self):
        self.client.get("/delay/0.1")
