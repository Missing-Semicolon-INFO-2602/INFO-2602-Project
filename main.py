from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading models, this may take a while...")
    print("Note: If this is the first time the app has been run, models will need to be downloaded and cached, future runs will be much faster")
    from inference import florence, bioclip
    app.state.florence = florence
    app.state.bioclip = bioclip
    print("Models loaded.")
    yield


app = FastAPI(title="CID Florence", lifespan=lifespan)


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
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
