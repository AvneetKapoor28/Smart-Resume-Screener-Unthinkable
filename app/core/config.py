from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Pydantic model for managing application settings and environment variables.
    """
    # This will load the "GEMINI_API_KEY" from your .env file
    GEMINI_API_KEY: str

    # We'll default to Gemini 1.5 Flash - it's fast and powerful
    MODEL_ID: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a single, importable instance of the settings
settings = Settings()