from fastapi import FastAPI

from routes.auth import auth_router
from database import engine

import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get('/')
def index():
  return {"msg":"home"}

app.include_router(auth_router, prefix="/api/v1")


  
  
  
  
  
  
  
  
  
  
  
  
  
  
  # pip cache purge
  # pip config set global.no-cache-dir false