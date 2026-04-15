from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates
from app.models.requests import *
from app.database import add_user_animal


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
        name="homepage.html",
        context={
            "user": user
        }
    )


#decided not to use rn
# @router.post("/florence")
# def florence_infer(req: FlorenceRequest):
#     result = router.state.florence.infer(req.image_b64, req.task)
#     return result


@router.post("/bioclip")
def bioclip_infer(
    request: Request,
    user: AuthDep,
    db:SessionDep,
    req: BioclipRequest
):
    if not getattr(request.app.state, "bioclip", None):
        raise HTTPException(status_code=503, detail="BioCLIP model not loaded")
    try:
        result = request.app.state.bioclip.infer(req.image_b64, req.ranks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    def split_species_name(full_name: str) -> tuple[str, str]:
        if not full_name or not isinstance(full_name, str):
            return "", ""
        parts = full_name.strip().split()
        genus_name = parts[0] if parts else ""
        species_name = parts[1] if len(parts) > 1 else ""
        return genus_name, species_name

    species_prediction = result.get("species")
    if isinstance(species_prediction, list) and species_prediction:
        if isinstance(species_prediction[0], dict):
            full_species = species_prediction[0].get("species") or species_prediction[0].get("name") or ""
        else:
            full_species = str(species_prediction[0])
    else:
        full_species = species_prediction if isinstance(species_prediction, str) else ""

    genus, species = split_species_name(full_species)
    animal = add_user_animal(user, genus, species, req.image_b64)
    if not animal:
        raise HTTPException(status_code=404, detail="Could not identify animal")
    return {"species": animal.species, "common_name": animal.common_name, "pic": animal.pic}