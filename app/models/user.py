from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from pydantic import EmailStr, BaseModel
from app.models.user_animal import UserAnimal

if TYPE_CHECKING:
    from app.models.animal import Animal

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role:str = ""

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    animal: Optional["Animal"] = Relationship(back_populates='logger', link_model=UserAnimal)
    
class Admin(UserBase, table=True):    
    id: Optional[int] = Field(default=None, primary_key=True)
    # admin should be able to limit user access if they log more than like 50 animals per day (aka spam)