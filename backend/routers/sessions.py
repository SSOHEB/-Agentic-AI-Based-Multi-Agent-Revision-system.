from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["Sessions"])

# Provide an empty stub endpoint to allow fastapi to boot
@router.get("/stub")
async def stub():
    pass
