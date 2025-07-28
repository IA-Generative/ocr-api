from pydantic import BaseModel, ConfigDict


class InputForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    storage_file_path: str
    raw_filename: str
    content_type: str
    ext: str
    size: int
