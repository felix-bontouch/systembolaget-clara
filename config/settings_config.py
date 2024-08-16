import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional, Tuple, Type
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    environment: str = Field(default="development", env="ENVIRONMENT")
    openai_api_key: Optional[str] = Field(default=None)
    openai_chat_model: Optional[str] = Field(default=None)
    db_host: Optional[str] = Field(default=None)
    db_name: Optional[str] = Field(default=None)
    db_port: Optional[str] = Field(default=None)
    db_username: Optional[str] = Field(default=None)
    db_password: Optional[str] = Field(default=None)

    class Config:
        extra = "ignore" 

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings
    ) -> Tuple:
        
        #Check to see what the environment is set to, and get the variables accordingly.
        environment = os.getenv('ENVIRONMENT', 'production')
        if environment == "development" or environment == "production":
            return init_settings, env_settings, MountedSecrets(), file_secret_settings
        else:
            return init_settings, env_settings, MountedSecrets(), file_secret_settings

class MountedSecrets:
    def __call__(self) -> dict:
        try:
            secrets = {
                'openai_api_key': os.getenv('OPENAI_API_KEY'),
                'openai_chat_model': os.getenv('OPENAI_CHAT_MODEL'),
                "db_host" : os.getenv('DB_HOST'),
                "db_port": os.getenv('DB_PORT'),
                "db_name": os.getenv('DB_NAME'),
                "db_username": os.getenv('DB_USERNAME'),
                "db_password": os.getenv('DB_PASSWORD')
            }
        except Exception as e:
            raise Exception(f"Failed to load secrets: {e}")
        return secrets

# Initialize and load secrets based on the environment
settings = Settings()