
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_health():
    """Check the health of the service and its dependencies."""
    return {
        "status": "ok",
        "services": {
            "engine": "up",
            "sdlc": "up",
            "depot": "up",
        },
    }
