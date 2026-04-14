import base64
import tempfile
import time
from bioclip import TreeOfLifeClassifier, Rank, BIOCLIP_V1_MODEL_STR
import app.inference as inference  # leave this here to make sure HF_HOME is set before model loads

classifier = TreeOfLifeClassifier() # bioclip v2 ~1.6GB
# classifier = TreeOfLifeClassifier(model_str=BIOCLIP_V1_MODEL_STR) # bioclip v1 ~600MB

RANK_MAP = {r.name.lower(): r for r in Rank}

def infer(image_b64: str, ranks=["species"]) -> dict[str, list[dict]]:
    # valid ranks: "kingdom", "phylum", "class", "order", "family", "genus", "species"
    if ranks is None:
        ranks = list(RANK_MAP.keys())
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(base64.b64decode(image_b64))
        tmp_path = tmp.name
    results = {}
    for rank_str in ranks:
        key = rank_str.lower()
        if key not in RANK_MAP:
            raise ValueError(f"Invalid rank '{rank_str}'. Valid ranks: {list(RANK_MAP.keys())}")
        results[key] = classifier.predict(tmp_path, RANK_MAP[key])
    return results
