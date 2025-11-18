import time
from typing import Any, Callable, TypeVar, Dict, AsyncGenerator
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastappear.config import settings
from fastappear.utils.db import init_models, async_session, async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from fastappear.utils.logger import logger
import argparse
import shutil
import os

description = """
<Application_Name> API's
"""

log = logger()


async def create_default_admin_if_missing(session: AsyncSession) -> None:
    """No-op helper to create a default admin if it does not exist.

    This is intentionally lightweight — it logs the operation. Replace with your
    production logic (creating a seeded admin user) in a real application.
    """
    log.debug("checked for default admin (no-op)")
    return None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context.

    - initializes the DB models at startup
    - tries to create a default admin if missing (no-op in minimal setup)
    - disposes the async engine at shutdown
    """
    log.info("Starting <Application_Name> API...")
    await init_models()
    # create_default_admin_if_missing is optional; implement as a no-op if not available
    try:
        async with async_session() as session:
            await create_default_admin_if_missing(session)
    except NameError:
        log.debug("create_default_admin_if_missing not available, skipping")
    except Exception:
        log.exception("Failed to create default admin, continuing startup")

    log.info("Startup complete.")

    yield

    log.info("Shutting down <Application_Name> API...")
    # Properly dispose the underlying engine when shutting down
    try:
        await async_engine.dispose()
    except Exception:
        log.exception("Error on engine dispose")
    log.info("Shutdown complete.")


app = FastAPI(
    title="<Application_Name>",
    description=description,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path=settings.root_path,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)


@app.get("/", tags=["Health"])
async def health_check() -> Dict[str, str]:
    return {"status": "ok", "message": "<Application_Name> API is running"}


F = TypeVar("F", bound=Callable[..., Any])


@app.middleware("http")
async def process_time_log_middleware(
    request: Request, call_next: Callable[[Request], Any]
) -> Response:
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = str(round(time.time() - start_time, 3))
    response.headers["X-Process-Time"] = process_time
    log.info(
        "Method=%s Path=%s StatusCode=%s ProcessTime=%s",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )
    return response


## Minimal routers for demonstration
login_router = APIRouter(prefix="/auth", tags=["auth"])
register_router = APIRouter(prefix="/auth", tags=["auth"])


@login_router.post("/login")
async def _login() -> Dict[str, str]:
    return {"detail": "login endpoint (stub)"}


@register_router.post("/register")
async def _register() -> Dict[str, str]:
    return {"detail": "register endpoint (stub)"}


app.include_router(login_router)
app.include_router(register_router)


def main() -> None:
    parser = argparse.ArgumentParser(description="FastAppear - FastAPI application")
    parser.add_argument("--init", action="store_true", help="Initialize a new FastAppear project in the current directory")
    args = parser.parse_args()

    if args.init:
        init_project()
    else:
        run_server()


def init_project() -> None:
    """Initialize a new FastAppear project by copying template files."""
    template_dir = os.path.join(os.path.dirname(__file__), "template")
    if not os.path.exists(template_dir):
        print("Error: Template directory not found in package.")
        return

    current_dir = os.getcwd()
    for item in os.listdir(template_dir):
        src = os.path.join(template_dir, item)
        dst = os.path.join(current_dir, item)
        if os.path.exists(dst):
            print(f"Skipping {item}: already exists")
        else:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"Copied {item}")

    print("FastAppear project initialized!")


def run_server() -> None:
    """Run the FastAPI server."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    main()
