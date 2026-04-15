from fastapi import Request
from fastapi.responses import HTMLResponse
from . import router, templates


@router.get("/results", response_class=HTMLResponse)
def results_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="results.html",
    )
