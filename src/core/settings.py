from pydantic import BaseSettings


class Settings(BaseSettings):
    """Main settings of Application"""

    # APP settings
    title: str = 'RestaurantApplication'

    # DB settings
    database_url: str
    echo_mode: bool = False

    redis_host: str
    redis_port: int = 6379
    redis_db: int = 1

    # Test settings
    database_test_url: str

    redis_test_port: int
    redis_test_db: int = 2

    class Config:
        env_file = '.env'


def get_settings() -> Settings:
    return Settings()
