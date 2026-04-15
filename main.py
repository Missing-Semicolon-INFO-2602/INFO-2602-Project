import uvicorn
from fastapi import FastAPI, Request, status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import templates, static_files, router, api_router
from app.config import get_settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading BioCLIP, this may take a while...")
    print("Note: If this is the first time the app has been run, the model will need to be downloaded and cached, future runs will be much faster")
    try:
        from app.inference import bioclip
        app.state.bioclip = bioclip
        print("BioCLIP loaded.")
    except Exception as e:
        app.state.bioclip = None
        print(f"BioCLIP failed to load, /bioclip will return 503: {e}")

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

if __name__ == "__main__":
    uvicorn.run("main:app", host=get_settings().app_host, port=get_settings().app_port, reload=get_settings().env.lower()!="production")
