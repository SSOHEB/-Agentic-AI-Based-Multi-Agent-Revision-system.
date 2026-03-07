from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.user_schema import UserCreate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate) -> User:
        # 1. check if user exists by email
        existing_user = await self.repository.get_by_email(data.email)
        
        # 2. if exists return existing user
        if existing_user:
            return existing_user
            
        # 3. otherwise create a new User model
        new_user = User(
            email=data.email,
            name=data.name,
            firebase_uid=data.firebase_uid,
            is_active=True
        )
        
        # 4. call repository create method
        return await self.repository.create(new_user)
