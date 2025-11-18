import os

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILENAME = os.environ.get("DOTENV", "")

UNCONFIGURED = "unconfigured"


class Config(BaseSettings):
    """Configuration settings for the Avatar client.

    Attributes
    ----------
    STORAGE_ENDPOINT_URL : HttpUrl
        The storage endpoint URL for file uploads/downloads.
    AVATAR_VERIFY_COMPATIBILITY : bool
        Whether to verify client-server compatibility on authentication.
        Default is True.
    AVATAR_API_KEY : str | None
        Optional API key for authentication. When provided, this will be used
        instead of username/password authentication. Can be set via the
        AVATAR_API_KEY environment variable.
    """

    model_config = SettingsConfigDict(
        # https://pydantic-docs.helpmanual.io/usage/settings/#use-case-docker-secrets
        env_file=[ENV_FILENAME],
        extra="ignore",
    )

    STORAGE_ENDPOINT_URL: HttpUrl = HttpUrl(
        os.environ.get("STORAGE_ENDPOINT_URL", "https://www.octopize.app/storage")
    )
    AVATAR_VERIFY_COMPATIBILITY: bool = True
    AVATAR_API_KEY: str | None = None


def get_config() -> Config:
    """Get the config."""
    return Config()


config: Config = get_config()
