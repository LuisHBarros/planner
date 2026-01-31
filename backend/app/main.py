"""FastAPI app entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import event_bus
from app.api.exceptions import register_exception_handlers
from app.api.middleware.auth import JwtAuthMiddleware
from app.api.routes import auth, employees, invites, me, projects, schedule, tasks
from app.infrastructure.events.handlers.notification_handler import register_notification_handlers
from app.infrastructure.notifications.daily_report_job import start_daily_report_job
from app.infrastructure.notifications.notification_service import NotificationService


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(title="Planner Multiplayer API")

    app.add_middleware(JwtAuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
    app.include_router(invites.router, prefix="/api/invites", tags=["invites"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
    app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
    app.include_router(schedule.router, prefix="/api/schedule", tags=["schedule"])
    app.include_router(me.router, prefix="/api/me", tags=["me"])

    notification_service = NotificationService()
    register_notification_handlers(event_bus, notification_service)
    start_daily_report_job(event_bus)

    return app


app = create_app()
