from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.user_animal import UserAnimal
from . import router, templates


@router.get("/collection", response_class=HTMLResponse)
def collection_view(request: Request, user: AuthDep, db: SessionDep):
    user_animals = db.exec(
        select(UserAnimal)
        .where(UserAnimal.user_id == user.id)
        .options(selectinload(UserAnimal.animal))
        .order_by(UserAnimal.date_added.desc())
    ).all()
    return templates.TemplateResponse(
        request=request,
        name="collection.html",
        context={"user_animals": user_animals}
    )
