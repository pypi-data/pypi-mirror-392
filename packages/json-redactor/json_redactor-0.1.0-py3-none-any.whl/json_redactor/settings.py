import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SENSITIVE_MASK: str = os.getenv("SENSITIVE_MASK", "***REDACTED***")


def get_settings() -> Settings:
    # can be loaded dynamicall if we ever install it as a package and provide custom settings
    return Settings()
