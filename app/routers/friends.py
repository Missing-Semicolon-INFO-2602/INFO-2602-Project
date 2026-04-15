from fastapi import Request
from fastapi.responses import HTMLResponse
from . import router, templates


@router.get("/friends", response_class=HTMLResponse)
def friends_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="friends.html",
    )
