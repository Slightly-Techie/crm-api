from fastapi import FastAPI
from api.routes.auth import auth_router
from api.routes.skills import skill_route
from api.routes.profile_page import profile_route
from api.routes.feeds import feed_route
from api.routes.announcements import announcement_route
from db.database import engine
from db.database import Base
from fastapi.middleware.cors import CORSMiddleware
from db.database import create_roles
from api.routes.tags import tag_route
from api.routes.stacks  import stack_router


# Base.metadata.create_all(bind=engine)
create_roles()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://crm-web.fly.dev",
    "https://app.slightlytechie.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_origin_regex="https:\/\/.*\.uffizzi\.com",
    allow_methods=["GET", "POST", "PUT", "DELETE", "UPDATE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get('/')
def index():
    return {"msg": "home"}

@app.get('/inactive')
def redirect():
    return {"msg": "Your account would be activated after a successful interview, thank you for your patience"}


app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_route,prefix="/api/v1")
app.include_router(skill_route,prefix="/api/v1")
app.include_router(tag_route,prefix="/api/v1")
app.include_router(feed_route,prefix="/api/v1")
app.include_router(stack_router, prefix='/api/v1')
app.include_router(announcement_route,prefix="/api/v1")


# pip cache purge
# pip config set global.no-cache-dir false


