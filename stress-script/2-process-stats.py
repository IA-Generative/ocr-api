import os
from glob import glob
import json
import requests

URL = os.environ.get("STRESS_HOST")
LOG_FOLDER = "tests/data/logs"
stop = ["completed", "failed", "canceled", "timeout"]

stats = {}
if __name__ == "__main__":
    files = list(glob(os.path.join(LOG_FOLDER, "*.json")))
    tasks = []
    for file in files:
        with open(file) as f:
            tasks.append(json.load(f))
    sum_time = 0
    n_values = 0
    while len(tasks):
        print(f"Size of task {len(tasks)}")
        indices_to_del = []
        for i in range(len(tasks)):
            task = tasks[i]
            task_id = task["id"]

            response = requests.get(f"{URL}/tasks/{task_id}")
            if response.status_code == 200:
                json_response = response.json()
                status = json_response["status"]
                if status in stop:
                    if status not in stats:
                        stats[status] = {"time": 0, "n_values": 0}
                    t = json_response["updated_at"] - json_response["created_at"]
                    stats[status]["time"] += t
                    stats[status]["n_values"] += 1
                    indices_to_del.append(i)
                    for status in stats:
                        print(
                            f"{status} (#{stats[status].get('n_values')}) : {stats[status]['time'] / stats[status].get('n_values', 1)}s"
                        )

        indices_to_del.sort(reverse=True)
        for index in indices_to_del:
            del tasks[index]
