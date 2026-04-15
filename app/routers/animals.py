from sqlmodel import select
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.animal import Animal
from app.models.user_animal import UserAnimal
from app.utilities.tree import build_tree
from . import api_router


@api_router.get("/animals/tree")
def animals_tree(user: AuthDep, db: SessionDep):
    animals = db.exec(
        select(Animal).join(UserAnimal).where(UserAnimal.user_id == user.id)
    ).all()
    return build_tree(animals)
