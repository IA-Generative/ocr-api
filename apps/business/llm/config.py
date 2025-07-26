from pydantic_settings import BaseSettings


class OpenAISetting(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    INSTRUCT_MODEL_NAME: str
    VISION_MODEL: str = None
