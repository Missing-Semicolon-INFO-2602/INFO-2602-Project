from contextlib import asynccontextmanager
from select import select
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.dependencies.session import SessionDep
from app.models.animal import Animal
from app.utilities.security import AuthDep


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading models, this may take a while...")
    print("Note: If this is the first time the app has been run, models will need to be downloaded and cached, future runs will be much faster")
    #from inference import florence, bioclip
    #app.state.florence = florence
    #app.state.bioclip = bioclip
    print("Models loaded.")
    yield


app = FastAPI(title="CID Florence", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


class FlorenceRequest(BaseModel):
    image_b64: str
    task: str = "<CAPTION>"


class BioclipRequest(BaseModel):
    image_b64: str
    ranks: list[str] = None


@app.post("/florence")
def florence_infer(req: FlorenceRequest):
    result = app.state.florence.infer(req.image_b64, req.task)
    return result


@app.post("/bioclip")
def bioclip_infer(req: BioclipRequest):
    try:
        result = app.state.bioclip.infer(req.image_b64, req.ranks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

@app.get('/', response_class=RedirectResponse)
def homepage(request: Request):
    return templates.TemplateResponse(
          request=request, 
          name="homepage.html",)

@app.get('/collectionBACLLI', response_class=RedirectResponse)
def homepage(request: Request):
    return templates.TemplateResponse(
          request=request, 
          name="collection.html",)

@app.get('/profile', response_class=RedirectResponse)
def homepage(request: Request):
    return templates.TemplateResponse(
          request=request, 
          name="profile.html",)

@app.get('/results', response_class=RedirectResponse)
def homepage(request: Request):
    return templates.TemplateResponse(
          request=request, 
          name="results.html",)

@app.get('/leaderboard', response_class=RedirectResponse)
def homepage(request: Request):
    return templates.TemplateResponse(
          request=request, 
          name="leaderboard.html",)

@app.get('/friends', response_class=RedirectResponse)
def homepage(request: Request):
    return templates.TemplateResponse(
          request=request, 
          name="friends.html",)

@app.get('/collection')
def home_view(request: Request, user: AuthDep, db:SessionDep):
  animals = db.exec(select(Animal)).all()
  return templates.TemplateResponse(
          request=request, 
          name="index.html",
          context = {"animals" : animals}
      )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
