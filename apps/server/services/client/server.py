import requests
from src.logger import logger
import time
import os


class ServerClient:
    def __init__(
        self,
        base_url: str = os.getenv("SERVER_BASE_URL", "http://localhost:5000"),
        headers: dict[str, str] | None = {
            "Authorization": f"Bearer {os.getenv('SERVER_API_KEY', 'secret-api')}",
            "X-User-Id": os.getenv("SERVER_USER_ID", "test_user"),
        },
        blocking: bool = True,
    ):
        self.base_url = base_url
        self.headers = headers or {}
        self.blocking = blocking

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        method = method.lower()
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)

        if self.blocking:
            logger.debug(f"Request: {response.content}")
            response.raise_for_status()
        return response

    def get_health(self) -> dict:
        response = self.request("GET", "/api/health")
        return response.json()

    def get_task_by_id(self, task_id: str, task_type: str | None = None) -> dict:
        params = {"task_type": task_type} if task_type else {}
        response = self.request("GET", f"/api/tasks/{task_id}", params=params)
        return response.json()

    def get_task_by_content_hash(self, content_hash_value: str) -> dict:
        response = self.request("GET", f"/api/tasks/content/{content_hash_value}")
        return response.json()

    def update_task_by_id(self, task_id: str, task_type: str, update_data: dict) -> dict:
        response = self.request(
            "PATCH",
            f"/api/tasks/{task_id}",
            params={"task_type": task_type},
            json=update_data,
        )
        return response.json()

    def create_task(self, task_data: dict) -> dict:
        response = self.request("POST", "/api/tasks", json=task_data)
        return response.json()

    def upsert_chunks(self, chunks: list[dict], content_hash: str, replace: bool = False) -> list[dict]:
        if replace:
            self.delete_by_content_hash(content_hash)

        self.request("POST", f"/api/ocr-chunks/{content_hash}", json={"chunks": chunks})
        response = self.request("GET", f"/api/ocr-chunks/{content_hash}")
        return response.json()

    def delete_by_content_hash(self, content_hash: str) -> int:
        response = self.request("DELETE", f"/api/ocr-chunks/{content_hash}")
        return response.json().get("deleted", 0)

    def get_by_content_hash(self, content_hash: str) -> list[dict]:
        response = self.request("GET", f"/api/ocr-chunks/{content_hash}")
        return response.json()

    def submit_task(
        self,
        task_data: dict,
        task_name: str,
    ) -> dict:
        response = self.request(
            "POST",
            "/api/v1/tasks/submit",
            params={"task_name": task_name},
            json=task_data,
        )
        return response.json()

    def search_chunks(
        self,
        content_hash: str,
        query_vector: list[float],
        top_k: int | None = 5,
        threshold: float | None = None,
    ) -> list[dict]:
        response = self.request(
            "POST",
            f"/api/ocr-chunks/{content_hash}/search",
            json={"query_vector": query_vector, "top_k": top_k, "threshold": threshold},
        )
        return response.json()


if __name__ == "__main__":
    client = ServerClient(
        base_url=os.getenv("SERVER_BASE_URL", "http://localhost:5000"),
        headers={"Authorization": f"Bearer {os.getenv('SERVER_API_KEY', 'secret-api')}"},
    )
    health = client.get_health()
    print("Server health:", health)
    new_task = client.create_task(
        {
            "type": "ocr",
            "group_id": "group1",
            "status": "created",
            "parameters": {"language": "eng"},
        }
    )
    for _ in range(5):
        task = client.get_task_by_id(new_task["id"], new_task["type"])
        print("Task status:", task["status"])
        if task["status"] == "completed":
            break
        time.sleep(1)
        task = client.update_task_by_id(
            new_task["id"],
            new_task["type"],
            {"status": "completed", "percentage": 100.0},
        )
