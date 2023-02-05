from pydantic import BaseSettings


class Settings(BaseSettings):
    """Main settings of Application"""

    # APP settings
    title: str = "RestaurantApplication"

    # DB(SQL) settings
    database_url: str
    echo_mode: bool = False

    # DB(NoSQL) settings
    redis_host: str
    redis_port: int = 6379
    redis_db: int = 1

    # Broker settings
    broker_url: str

    # Test settings
    database_test_url: str

    redis_test_cache: str
    redis_test_db: int = 2

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
