import os
from glob import glob
import json
import requests
from src.schemas.task import TaskModel, TaskStatus

URL = os.environ.get("STRESS_HOST")
LOG_FOLDER = "tests/data/logs"
stop = [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, 
        TaskStatus.CANCELED.value, TaskStatus.TIMEOUT.value]

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
                task = TaskModel.model_validate(json_response)
                status = task.status
                if status in stop:
                    if status not in stats:
                        stats[status] = {"time": 0, "n_values": 0, 'time_process': 0}
                        
                    if status == TaskStatus.COMPLETED.value:
                        stats[status]['time_process'] += task.output.updated_at - task.output.created_at
                    t = task.updated_at - task.created_at
                    stats[status]["time"] += t
                    stats[status]["n_values"] += 1
                    indices_to_del.append(i)
                    time_process=stats[status]['time_process']
                    time_f = stats[status]['time']
                    n_values = stats[status].get('n_values', 1)
                    for status in stats:
                        print(
                            f"{status} (#{n_values}) : {time_f /n_values}s - time_process: {time_process/n_values}"
                        )

        indices_to_del.sort(reverse=True)
        for index in indices_to_del:
            del tasks[index]
