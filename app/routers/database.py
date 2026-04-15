from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlmodel import select, or_
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.animal import Animal
from . import router, templates


@router.get("/database", response_class=HTMLResponse)
def database_view(request: Request, user: AuthDep, db: SessionDep, q: str = ""):
    qry = select(Animal)
    if q:
        like = f"%{q}%"
        qry = qry.where(or_(Animal.common_name.ilike(like), Animal.species.ilike(like)))
    animals = db.exec(qry).all()
    return templates.TemplateResponse(
        request=request,
        name="database.html",
        context={"animals": animals, "q": q}
    )
