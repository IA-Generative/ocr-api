#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "locust",
# ]

from locust import HttpUser, task, between
import os
import random
import mimetypes
import json
import os

VALID_DIR = "tests/data/valid"
LOG_FOLDER = "tests/data/logs"
os.makedirs(LOG_FOLDER, exist_ok=True)


class UploadFileUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.client.proxies = {
            "http": os.environ.get("http_proxy"),
            "https": os.environ.get("https_proxy"),
            "no": os.environ.get("no_proxy"),
        }

    def get_random_file(self):
        files = [
            os.path.join(VALID_DIR, f) for f in os.listdir(VALID_DIR) if os.path.isfile(os.path.join(VALID_DIR, f))
        ]
        return random.choice(files) if files else None

    def get_mime_type(self, filepath):
        mime_type, _ = mimetypes.guess_type(filepath)
        return mime_type or "application/octet-stream"

    @task
    def upload_file(self):
        user_id = "1234"
        file_path = self.get_random_file()

        if not file_path:
            print("Aucun fichier trouvé dans le dossier 'valid'")
            return

        mime_type = self.get_mime_type(file_path)

        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, mime_type)}
            response = self.client.post(f"/jobs/{user_id}", files=files)
            if response.status_code == 201:
                data_json = response.json()
                with open(os.path.join(LOG_FOLDER, f"{data_json['id']}.json"), "w") as f:
                    json.dump(data_json, f, indent=2)
