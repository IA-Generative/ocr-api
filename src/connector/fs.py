import os
import shutil
from .base import BaseFileConnector


class FileSystemConnector(BaseFileConnector):
    def __init__(self, base_folder: str = "./tmp"):
        super().__init__()
        self.__folder = base_folder
        os.makedirs(self.__folder, exist_ok=True)

    def get_by_task_id(self, user_id: str, task_id: str) -> str:
        folder_task = os.path.join(self.__folder, user_id, task_id)
        if os.path.exists(folder_task):
            return folder_task
        else:
            raise FileNotFoundError(
                f"Fichiers pour la tâche {task_id} de l'utilisateur {user_id} non trouvés."
            )

    def save(self, user_id: str, task_id: str, file_path: str) -> str:
        folder_task = os.path.join(self.__folder, user_id, task_id)
        os.makedirs(folder_task, exist_ok=True)
        file_name = os.path.basename(file_path)
        destination_path = os.path.join(folder_task, file_name)

        shutil.copy2(file_path, destination_path)

        return destination_path

    def delete_by_task_id(self, user_id: str, task_id: str) -> bool:
        folder_task = os.path.join(self.__folder, user_id, task_id)
        if os.path.exists(folder_task):
            shutil.rmtree(folder_task)
            return True
        return False

    def delete_by_user_id(self, user_id: str) -> bool:
        folder_user = os.path.join(self.__folder, user_id)
        if os.path.exists(folder_user):
            shutil.rmtree(folder_user)
            return True
        return False
