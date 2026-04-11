from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING
from pydantic import EmailStr, BaseModel

# attributes for all taxonomic levels
# date logged
if TYPE_CHECKING:
    from app.models.user import User

# class AnimalBase(SQLModel):
#     animal_id: int
#     name: str
    
class Animal(SQLModel, table=True):
      animal_id: Optional[int] =  Field(default=None, primary_key=True)
      kingdom: Optional[str] = Field(index=True)
      phylum: Optional[str] = Field(index=True)
      classTaxonomic: Optional[str] = Field(index=True)   #yikes
      order: Optional[str] = Field(index=True)
      family: Optional[str] = Field(index=True)
      genus: Optional[str] = Field(index=True)
      species: Optional[str] = Field(index=True)
      logger: "User" = Relationship(back_populates="animal", link_model=UserAnimal)