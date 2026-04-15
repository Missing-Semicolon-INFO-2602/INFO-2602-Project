from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
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
    users = db.exec(select(User).order_by(User.weekly_points.desc())).all() #makes templating easier
    return templates.TemplateResponse(
        request=request, 
        name="leaderboard.html",
        context={
            "users": users
        }
    )

