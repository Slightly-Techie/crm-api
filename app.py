from fastapi import FastAPI
from api.routes.auth import auth_router
from db.database import engine
from db.database import Base
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://crm-web.fly.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def index():
    return {"msg": "home"}


app.include_router(auth_router, prefix="/api/v1")


# pip cache purge
# pip config set global.no-cache-dir false
