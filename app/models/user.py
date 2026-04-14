from datetime import date, timedelta
from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional, TYPE_CHECKING
from pydantic import EmailStr, model_validator
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
    animals: List["Animal"] = Relationship(back_populates='logger', link_model=UserAnimal)
    weekly_points: Optional[int] = Field(default=0)
    
    @model_validator(mode="after")
    def get_weekly_points(self) -> int:
        today = date.today()
        days_since_sunday = (today.weekday() - 6) % 7
        week_start = today - timedelta(days=days_since_sunday)

        if not self.animals:
            self.weekly_points=0

        count=sum(
            1 for animal in self.animals
            if getattr(animal, 'date_added', None) is not None
            and getattr(animal.date_added, 'date', None) is not None
            and animal.date_added.date() >= week_start
        )
        self.weekly_points=count
    
class Admin(UserBase, table=True):    
    id: Optional[int] = Field(default=None, primary_key=True)
    # admin should be able to limit user access if they log more than like 50 animals per day (aka spam)