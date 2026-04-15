from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates
from app.models.user import User

@router.get("/leaderboard")
async def user_home_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    users = db.exec(select(User).options(selectinload(User.user_animals))).all()
    users = sorted(users, key=lambda u: u.weekly_points or 0, reverse=True) #dedup happens in validator, sort here after eager load
    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={
            "users": users
        }
    )

