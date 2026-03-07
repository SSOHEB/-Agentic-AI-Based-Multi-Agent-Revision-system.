from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    """
    Schema for validating the creation of a new user.
    """
    email: EmailStr
    name: str
    firebase_uid: str

class UserResponse(BaseModel):
    """
    Schema for validating the response containing user details.
    """
    id: UUID
    email: EmailStr
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
