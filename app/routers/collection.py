from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlmodel import select
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from app.models.animal import Animal
from . import router, templates


@router.get("/collection", response_class=HTMLResponse)
def collection_view(request: Request, user: AuthDep, db: SessionDep):
    animals = db.exec(select(Animal)).all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"animals": animals}
    )


@router.get("/collectionBACLLI", response_class=HTMLResponse)
def collection_backup_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="collection.html",
    )
