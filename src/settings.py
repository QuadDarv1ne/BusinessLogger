from typing import Optional
from pydantic import SecretStr, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(BaseSettings):
    """
    Базовый класс для чтения переменных окружения из файла .env.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

class Settings(Environment):
    """
    Настройки приложения.
    """
    # Настройки Redis
    REDIS_HOST: str = Field(default="localhost", description="Адрес Redis-сервера")
    REDIS_PORT: int = Field(default=6379, description="Порт Redis-сервера")
    REDIS_PASSWORD: Optional[SecretStr] = Field(default=None, description="Пароль для Redis")

    # Настройки бота
    TOKEN: SecretStr = Field(..., description="Токен Telegram-бота (обязательно)")
    USER_ID: int = Field(..., description="ID администратора бота (обязательно)")

# Инициализация настроек
try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Ошибка в настройках: {e}")
