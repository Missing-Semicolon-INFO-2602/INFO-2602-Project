import base64
import io
import torch
from PIL import Image
from bioclip.predict import TreeOfLifeClassifier, Rank
import app.inference as inference  # leave this here to make sure HF_HOME is set before model loads

_device = "cuda:0" if torch.cuda.is_available() else "cpu"
classifier = TreeOfLifeClassifier(device=_device) # species only, GPU if available

def infer(image_b64: str) -> dict[str, list[dict]]:
    image = Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")
    predictions = classifier.predict([image], Rank.SPECIES, k=1, batch_size=1)
    return {"species": predictions}

def warmup():
    buf = io.BytesIO()
    Image.new("RGB", (224, 224), color=(0, 0, 0)).save(buf, format="JPEG")
    infer(base64.b64encode(buf.getvalue()).decode())
