from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Ollama
    ollama_api_base: str = "http://localhost:11434"
    ollama_model: str = "gemma4:e4b"

    # App
    app_name: str = "Karma Backend"
    app_port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: list[str] = ["*"]


settings = Settings()
