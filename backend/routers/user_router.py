from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db
from backend.repositories.user_repository import UserRepository
from backend.schemas.user_schema import UserCreate, UserResponse
from backend.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    repository = UserRepository(db)
    service = UserService(repository)
    return await service.create_user(user_data)
