from fastapi import FastAPI
from api.routes.auth import auth_router
from api.routes.skills import skill_route
from api.routes.profile_page import profile_route
from api.routes.feeds import feed_route
from api.routes.techieotm import techieotm_router
from api.routes.announcements import announcement_route
from db.database import engine
from db.database import Base
from fastapi.middleware.cors import CORSMiddleware
from utils.s3 import create_bucket
from db.database import create_roles
from api.routes.tags import tag_route
from api.routes.stacks  import stack_router
from api.routes.project import project_router
from fastapi_pagination import add_pagination


# Base.metadata.create_all(bind=engine)
create_roles()

app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:3000",
#     "https://crm-web.fly.dev",
#     "https://app.slightlytechie.com"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_origin_regex="https:\/\/.*\.uffizzi\.com",
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await create_bucket()

@app.get('/')
def index():
    return {"msg": "home"}

@app.get('/inactive')
def redirect():
    return {"msg": "Your account would be activated after a successful interview, thank you for your patience"}  # noqa: E501


app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_route,prefix="/api/v1")
app.include_router(skill_route,prefix="/api/v1")
app.include_router(tag_route,prefix="/api/v1")
app.include_router(feed_route,prefix="/api/v1")
app.include_router(techieotm_router, prefix="/api/v1")
app.include_router(stack_router, prefix='/api/v1')
app.include_router(announcement_route,prefix="/api/v1")
app.include_router(project_router,prefix="/api/v1")

add_pagination(app)

# pip cache purge
# pip config set global.no-cache-dir false


