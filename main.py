
from fastapi import FastAPI
from core.config import settings
from db.session import  engine,get_db
from db.base import Base
import asyncio
from apis.version1.onboarding  import router as onboarding_router
from apis.version1.test  import router as testing_router
<<<<<<< HEAD
from apis.version1.encryption import app as encryption_router
=======
from apis.version1.encyption import router as encryption_router
from apis.version1.middleware import decryptMiddleware
<<<<<<< HEAD
>>>>>>> e10627c098a970e5e0ee6867dd24c0935eb2bfa7
=======
>>>>>>> 6bdea9418ab9bfa3a011ac6d6bb29f1eebfc3a23

active_session = {}


def create_tables():
    Base.metadata.create_all(bind=engine)

def startapplication():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION,docs_url=None, redoc_url=None)
    app.add_middleware(decryptMiddleware)
    app.include_router(onboarding_router)
    app.include_router(testing_router)
    app.include_router(encryption_router)

    db = next(get_db()) 

    create_tables()
    return app


app = startapplication()





