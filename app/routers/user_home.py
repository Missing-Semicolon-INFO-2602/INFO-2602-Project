from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates
from app.models.requests import *


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    if await is_admin(user):
        return RedirectResponse(url=request.url_for("admin_home_view"), status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse(
        request=request, 
        name="app.html",
        context={
            "user": user
        }
    )
    
    
# adding an animal
@router.post("/florence")
def florence_infer(req: FlorenceRequest):
    result = router.state.florence.infer(req.image_b64, req.task)
    return result


@router.post("/bioclip")
def bioclip_infer(req: BioclipRequest):
    try:
        result = router.state.bioclip.infer(req.image_b64, req.ranks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result