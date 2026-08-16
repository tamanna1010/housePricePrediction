from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    # Azure OpenAI
    AZURE_OPENAI_API_KEY = os.getenv(
        "AZURE_OPENAI_API_KEY"
    )

    AZURE_OPENAI_API_BASE = os.getenv(
        "AZURE_OPENAI_API_BASE"
    )

    AZURE_OPENAI_API_VERSION = os.getenv(
        "AZURE_OPENAI_API_VERSION"
    )

    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    )

    # Redis
    REDIS_HOST = os.getenv(
        "REDIS_HOST",
        "localhost"
    )

    REDIS_PORT = int(
        os.getenv(
            "REDIS_PORT",
            6379
        )
    )

    # Vector DB
    VECTOR_DB_PATH = "./chroma_db"


settings = Settings()