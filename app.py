from fastapi import FastAPI

from api.routes.auth import auth_router
from db.database import engine

from db.database import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get('/')
def index():
    return {"msg": "home"}


app.include_router(auth_router, prefix="/api/v1")

# pip cache purge
# pip config set global.no-cache-dir false
