from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone, timedelta

if TYPE_CHECKING:
    from app.models.animal import Animal
    from app.models.user import User

class UserAnimal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    animal_id: int = Field(foreign_key="animal.animal_id")
    date_added: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=-4))))
    date_added_str: str = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=-4))).strftime("%d/%m/%y"))
    user_pic: str   # can store and display pic that user uploaded to app
    user: Optional["User"] = Relationship(back_populates='user_animals')
    animal: Optional["Animal"] = Relationship(back_populates='logger')