#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "locust",
# ]


from locust import HttpUser, task, between
import uuid


class OCRUser(HttpUser):
    wait_time = between(
        1, 3
    )  # Temps d'attente entre les requêtes pour chaque utilisateur

    @task
    def upload_image(self):
        # Charger une image test depuis le disque
        file_path = (
            "tests/data/valid/cerfa_13750-05-1.pdf"  # Assure-toi que ce fichier existe
        )
        with open(file_path, "rb") as f:
            files = {"file": (f"{str(uuid.uuid4())}.pdf", f, "application/pdf")}
            data = {
                "grayscale": "true",
                "return_image": "false",
            }
            self.client.post("/", files=files, data=data)
