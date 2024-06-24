
from fastapi import FastAPI
from core.config import settings
from db.session import  engine,get_db
from db.base import Base
import asyncio
from apis.version1.onboarding  import router as onboarding_router
from apis.version1.test  import router as testing_router
from apis.version1.encryption import app as encryption_router

active_session = {}


def create_tables():
    Base.metadata.create_all(bind=engine)

def startapplication():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION,docs_url=None, redoc_url=None)
    app.include_router(onboarding_router)
    app.include_router(testing_router)
    app.include_router(encryption_router)

    db = next(get_db()) 

    create_tables()
    return app


app = startapplication()





