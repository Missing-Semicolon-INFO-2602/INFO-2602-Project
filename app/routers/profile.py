from fastapi import Request
from fastapi.responses import HTMLResponse
from . import router, templates


@router.get("/profile", response_class=HTMLResponse)
def profile_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
    )
