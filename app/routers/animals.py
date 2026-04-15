from sqlmodel import select
from app.dependencies.session import SessionDep
from app.models.animal import Animal
from app.utilities.tree import build_tree
from . import api_router


@api_router.get("/animals/tree")
def animals_tree(db: SessionDep):
    animals = db.exec(select(Animal)).all()
    return build_tree(animals)
