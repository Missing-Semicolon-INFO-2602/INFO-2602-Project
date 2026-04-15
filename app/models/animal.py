from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_animal import UserAnimal

    
class Animal(SQLModel, table=True):
      animal_id: int =  Field(default=None, primary_key=True)
      kingdom: str = Field(index=True)
      phylum: str = Field(index=True)
      class_: str = Field(index=True)   #yikes
      order: str = Field(index=True)
      family: str = Field(index=True)
      species: str = Field(index=True)
      common_name: str = Field(index=True)
      pic: str = Field(default="")
      user_animals: List["UserAnimal"] = Relationship(back_populates='animal')