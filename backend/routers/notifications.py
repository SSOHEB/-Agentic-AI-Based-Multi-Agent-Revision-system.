from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Provide an empty stub endpoint to allow fastapi to boot
@router.get("/stub")
async def stub():
    pass
