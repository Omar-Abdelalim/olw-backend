
from fastapi import FastAPI
from core.config import settings
from db.session import  engine,get_db
from db.base import Base
import asyncio
from apis.version1.onboarding  import router as onboarding_router


def create_tables():
    Base.metadata.create_all(bind=engine)

def startapplication():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION,docs_url=None, redoc_url=None)
    app.include_router(onboarding_router)
    
    db = next(get_db()) 

    create_tables()
    return app


app = startapplication()





