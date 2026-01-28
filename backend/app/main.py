"""FastAPI application factory and startup wiring."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.infrastructure.database import engine, Base, get_db
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.events.handlers.dependency_handler import DependencyHandler
from app.infrastructure.i18n.translation_service import TranslationService
from app.infrastructure.persistence.repositories import (
    SqlAlchemyCompanyRepository,
    SqlAlchemyTeamRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyTaskRepository,
    SqlAlchemyTaskDependencyRepository,
    SqlAlchemyNoteRepository,
)
from app.api.routes import companies, teams, roles, projects, tasks
from app.api.exceptions import setup_exception_handlers


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        debug=settings.debug,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Initialize database tables (for development)
    if settings.env == "development":
        Base.metadata.create_all(bind=engine)

    # Initialize services on startup
    @app.on_event("startup")
    async def on_startup() -> None:  # pragma: no cover - side-effect wiring
        # Create a short-lived session just for wiring repositories into handlers
        db: Session = next(get_db())
        task_repo = SqlAlchemyTaskRepository(db)
        dep_repo = SqlAlchemyTaskDependencyRepository(db)

        # Initialize event bus and register handlers
        event_bus = InMemoryEventBus()
        dependency_handler = DependencyHandler(event_bus, task_repo, dep_repo)
        dependency_handler.register()

        app.state.event_bus = event_bus
        app.state.translation_service = TranslationService()

    # Include routers
    app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
    app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
    app.include_router(roles.router, prefix="/api/roles", tags=["roles"])
    app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

    return app


app = create_app()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Planner API", "version": settings.api_version}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
