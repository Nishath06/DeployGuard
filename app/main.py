import os
from fastapi import FastAPI, Response, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="DeployGuard Demo App",
    description="Production-Ready DevOps Blue/Green Deployment Demo Application",
    version="1.0.0"
)

# Base directory relative resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static files and Jinja2 templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def get_deployment_config():
    """Extract deployment metadata from environment variables with sensible defaults."""
    force_unhealthy_raw = os.getenv("FORCE_UNHEALTHY", "false").strip().lower()
    is_force_unhealthy = force_unhealthy_raw in ("true", "1", "yes")

    return {
        "application": "DeployGuard",
        "version": os.getenv("APP_VERSION", "dev"),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "deployment_slot": os.getenv("DEPLOYMENT_SLOT", "LOCAL").upper(),
        "commit": os.getenv("COMMIT_SHA", "unknown"),
        "build_number": os.getenv("BUILD_NUMBER", "0"),
        "force_unhealthy": is_force_unhealthy,
    }


@app.get("/")
async def read_root(request: Request):
    """Render the DeployGuard SRE Dashboard landing page."""
    config = get_deployment_config()
    is_healthy = not config["force_unhealthy"]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "config": config,
            "is_healthy": is_healthy,
            "status_label": "HEALTHY" if is_healthy else "UNHEALTHY",
        }
    )


@app.get("/health")
async def health_check(response: Response):
    """
    Health check endpoint for AWS ECS / ALB deployment validation.
    Returns HTTP 200 when healthy, HTTP 503 when FORCE_UNHEALTHY=true.
    """
    config = get_deployment_config()

    if config["force_unhealthy"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy"}

    response.status_code = status.HTTP_200_OK
    return {"status": "healthy"}


@app.get("/version")
async def version_info():
    """Return JSON version & deployment metadata."""
    config = get_deployment_config()
    return {
        "application": config["application"],
        "version": config["version"],
        "environment": config["environment"],
        "deployment_slot": config["deployment_slot"],
        "commit": config["commit"],
        "build_number": config["build_number"],
    }


@app.get("/api/info")
async def api_info():
    """Return complete metadata including current operational health state."""
    config = get_deployment_config()
    is_healthy = not config["force_unhealthy"]
    return {
        **config,
        "health_status": "healthy" if is_healthy else "unhealthy",
    }
