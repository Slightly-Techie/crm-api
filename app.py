import logging
from fastapi import FastAPI, HTTPException
from api.routes.auth import auth_router
from api.routes.email_templates import email_templates_route
from api.routes.skills import skill_route
from api.routes.profile_page import profile_route
from api.routes.feeds import feed_route
from api.routes.techieotm import techieotm_router
from api.routes.announcements import announcement_route
from api.routes.weekly_meetings import weekly_meeting_route
from api.routes.coding_challenges import coding_challenge_route

# from db.database import engine
# from db.database import Base
from fastapi.middleware.cors import CORSMiddleware
from db.database import create_roles, create_stacks, SessionLocal
from api.routes.tags import tag_route
from api.routes.stacks import stack_router
from api.routes.project import project_router
from api.routes.technical_task import tech_task_router, sub_tech_task_router
from fastapi_pagination import add_pagination
from api.routes.endpoints import endpoints_route
from api.routes.users import users_route
from utils.endpoints_status import create_signup_endpoint
from sqlalchemy import text

# Base.metadata.create_all(bind=engine)


logger = logging.getLogger(__name__)


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://crm-web.fly.dev",
    "https://app.slightlytechie.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_origin_regex=r"https://.*\.uffizzi\.com",
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


@app.get(
    "/api/v1/health",
    responses={500: {"description": "Service health check failed"}}
)
def health_check():
    """Health check endpoint - accessible without authentication"""
    db = SessionLocal()
    try:
        # Lightweight DB liveness probe without exposing operational metrics.
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "Service is healthy"
        }
    except Exception:
        logger.exception("Health check failed")
        raise HTTPException(
            status_code=500,
            detail={"status": "unhealthy", "message": "Service is unhealthy"}
        )
    finally:
        db.close()


async def startup_event():
    create_roles()
    create_stacks()
    create_signup_endpoint()


v1_prefix = "/api/v1"

app.add_event_handler("startup", startup_event)
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
app.include_router(users_route, prefix=v1_prefix)
app.include_router(weekly_meeting_route, prefix=v1_prefix)
app.include_router(coding_challenge_route, prefix=v1_prefix)

add_pagination(app)

# pip cache purge
# pip config set global.no-cache-dir false
