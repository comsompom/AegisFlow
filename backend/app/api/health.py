from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    return {"ready": True}
