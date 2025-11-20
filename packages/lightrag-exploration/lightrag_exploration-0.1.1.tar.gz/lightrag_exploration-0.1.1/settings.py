from pydantic_settings import BaseSettings

class LocalSettings(BaseSettings):
    research_output_dir: str
    ollama_host: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"