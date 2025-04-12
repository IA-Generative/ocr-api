from .config.fs import FileSystemSettings
from src.connector.fs import FileSystemConnector

fs_settings = FileSystemSettings()
fs_connector = FileSystemConnector(base_folder=fs_settings.FOLDER)
