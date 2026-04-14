from pydantic import BaseModel

class FlorenceRequest(BaseModel):
    image_b64: str
    task: str = "<CAPTION>"

class BioclipRequest(BaseModel):
    image_b64: str
    ranks: list[str] = None