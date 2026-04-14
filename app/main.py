import uvicorn
from fastapi import FastAPI, Request, status, HTTPException
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import templates, static_files, router, api_router
from app.config import get_settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # print("Loading models, this may take a while...")
    # print("Note: If this is the first time the app has been run, models will need to be downloaded and cached, future runs will be much faster")
    # from app.inference import florence, bioclip
    # app.state.florence = florence
    # app.state.bioclip = bioclip
    # print("Models loaded.")
    
    from app.database import init
    init()
    yield
    
    
app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key=get_settings().secret_key)
],
    title="CID Florence",
    lifespan=lifespan
)   

app.include_router(router)
app.include_router(api_router)
app.mount("/static", static_files, name="static")

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_redirect_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request, 
        name="401.html",
    )
    

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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=get_settings().app_host, port=get_settings().app_port, reload=get_settings().env.lower()!="production")