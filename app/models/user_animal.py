from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from pydantic import EmailStr, BaseModel
from datetime import datetime

if TYPE_CHECKING:
    from app.models.animal import Animal
    from app.models.user import User

class UserAnimal(SQLModel, table=True):
    id: Optional[int] =  Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    animal_id: int = Field(foreign_key="animal.animal_id")
    