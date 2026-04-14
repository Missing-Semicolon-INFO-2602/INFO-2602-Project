from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from pydantic import EmailStr, BaseModel
from app.models.user_animal import UserAnimal

# attributes for all taxonomic levels
# date logged
if TYPE_CHECKING:
    from app.models.user import User

# class AnimalBase(SQLModel):
#     animal_id: int
#     name: str
    
class Animal(SQLModel, table=True):
      animal_id: int =  Field(default=None, primary_key=True)
      kingdom: str = Field(index=True)
      phylum: str = Field(index=True)
      class_: str = Field(index=True)   #yikes
      order: str = Field(index=True)
      family: str = Field(index=True)
      genus: str = Field(index=True)
      species: str = Field(index=True)
      common_name: str = Field(index=True)
      logger: "User" = Relationship(back_populates="animals", link_model=UserAnimal)