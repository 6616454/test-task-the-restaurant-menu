from pydantic import BaseSettings


class Settings(BaseSettings):
    """Main settings of Application"""

    # APP settings
    title: str = 'RestaurantApplication'

    # DB settings
    database_url: str
    echo_mode: bool = False

    class Config:
        env_file = '.env'


def get_settings() -> Settings:
    return Settings()
