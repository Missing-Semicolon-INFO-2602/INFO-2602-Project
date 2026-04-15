from datetime import date, timedelta
from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional, TYPE_CHECKING
from pydantic import EmailStr, model_validator
from app.models.user_animal import UserAnimal

if TYPE_CHECKING:
    from app.models.user_animal import UserAnimal

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role:str = ""

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role:str = "user"
    user_animals: List["UserAnimal"] = Relationship(back_populates='user')
    weekly_points: Optional[int] = Field(default=0)
    
    @model_validator(mode="after")
    def get_weekly_points(self) -> "User":
        today = date.today()
        days_since_sunday = (today.weekday() - 6) % 7
        week_start = today - timedelta(days=days_since_sunday)

        if not self.user_animals:
            self.weekly_points = 0
            return self

        count = sum(
            1 for user_animal in self.user_animals
            if getattr(user_animal, 'date_added', None) is not None
            and user_animal.date_added.date() >= week_start
        )
        self.weekly_points = count
        return self
    
class Admin(UserBase, table=True):    
    id: Optional[int] = Field(default=None, primary_key=True)
    role:str = "admin"
    # admin should be able to limit user access if they log more than like 50 animals per day (aka spam)