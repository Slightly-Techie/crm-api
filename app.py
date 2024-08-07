from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.routes.auth import auth_router
from api.routes.email_templates import email_templates_route
from api.routes.skills import skill_route
from api.routes.profile_page import profile_route
from api.routes.feeds import feed_route
from api.routes.techieotm import techieotm_router
from api.routes.announcements import announcement_route

# from db.database import engine
# from db.database import Base
from fastapi.middleware.cors import CORSMiddleware
from utils.s3 import create_bucket
from db.database import create_roles
from api.routes.tags import tag_route
from api.routes.stacks import stack_router
from api.routes.project import project_router
from api.routes.technical_task import tech_task_router, sub_tech_task_router
from fastapi_pagination import add_pagination
from api.routes.endpoints import endpoints_route
from utils.endpoints_status import create_signup_endpoint

# Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_bucket()
    yield


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


@app.get("/")
def index():
    return {"msg": "home"}


@app.get("/inactive")
def redirect():
    return {
        "msg": "Your account would be activated after a successful interview, thank you for your patience"
    }  # noqa: E501


async def startup_event():
    create_roles()
    create_signup_endpoint()


v1_prefix = "/api/v1"

# app.add_event_handler("startup", startup_event)
app.include_router(auth_router, prefix=v1_prefix)
app.include_router(profile_route, prefix=v1_prefix)
app.include_router(skill_route, prefix=v1_prefix)
app.include_router(tag_route, prefix=v1_prefix)
app.include_router(feed_route, prefix=v1_prefix)
app.include_router(techieotm_router, prefix=v1_prefix)
app.include_router(stack_router, prefix=v1_prefix)
app.include_router(announcement_route, prefix=v1_prefix)
app.include_router(project_router, prefix=v1_prefix)
app.include_router(tech_task_router, prefix=v1_prefix)
app.include_router(sub_tech_task_router, prefix=v1_prefix)
app.include_router(email_templates_route, prefix=v1_prefix)
app.include_router(endpoints_route, prefix=v1_prefix)

add_pagination(app)

# pip cache purge
# pip config set global.no-cache-dir false
