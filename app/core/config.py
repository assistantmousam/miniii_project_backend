# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     APP_NAME: str = "DSA Arcade API"
#     APP_VERSION: str = "1.0.0"
#     DEBUG: bool = True

#     DATABASE_URL: str

#     JWT_SECRET_KEY: str
#     JWT_ALGORITHM: str = "HS256"

#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
#     REFRESH_TOKEN_EXPIRE_DAYS: int = 7

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore",
#     )


# settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "DSA Arcade API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173"
    )

    RATE_LIMIT_LOGIN: int = 5
    RATE_LIMIT_REGISTER: int = 3

    INACTIVITY_TIMEOUT_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()