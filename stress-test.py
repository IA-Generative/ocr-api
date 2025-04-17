#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "locust",
# ]


from locust import HttpUser, task, between
import os


class UploadFileUser(HttpUser):
    wait_time = between(1, 5)  # temps d'attente entre chaque tâche (sec)

    @task
    def upload_file(self):
        user_id = "1234"
        file_path = "tests/data/valid/cerfa_13750-05-1.pdf"

        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f, "application/pdf")
            }

            self.client.post(f"/jobs/{user_id}", files=files)
