import os
from pathlib import Path
from dotenv import load_dotenv

path_env=Path('.')/".env"
load_dotenv(dotenv_path=path_env)
class Settings:
    PROJECT_NAME :str="One Limit Wallet"
    PROJECT_VERSION:str="0.1"
    POSTGRES_USER:str=os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD:str=os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER:str=os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT:str=os.getenv("POSTGRES_PORT")
    POSTGRES_DB:str=os.getenv(("POSTGRES_DB"))
    # DATABASE_URL = "sqlite:///./sql_app.db"
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SECRET_KEY:str=os.getenv('SECRET_KEY')
    ALGORITHM:str=os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES=30
settings=Settings()