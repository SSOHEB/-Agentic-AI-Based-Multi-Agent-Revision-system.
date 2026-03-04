from fastapi import APIRouter

router = APIRouter(prefix="/topics", tags=["Topics"])

# Provide an empty stub endpoint to allow fastapi to boot
@router.get("/stub")
async def stub():
    pass
