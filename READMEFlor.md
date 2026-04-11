# CID Florence

A FastAPI application for animal/species identification using two vision models:

- **Florence-2-base-ft** (Microsoft) - image captioning and object detection
- **BioCLIP v2** (Imageomics) - taxonomic classification at any rank

## Models

| Model / Data | Size | Purpose | Speed (CPU) |
|-------|------|---------|-------------|
| Florence-2-base-ft | ~445 MB | Captioning, object detection, OCR | ~16s per image |
| BioCLIP v2 (ViT-L/14) | ~1.6 GB | Species/taxonomy classification | ~9s (all 7 ranks) |
| TreeOfLife-200M | ~2.6 GB | Taxonomy labels and precomputed text embeddings for BioCLIP's 952K taxa | Downloaded automatically on first run |

### Memory requirements

Both models are loaded into RAM at startup and stay resident for the lifetime of the server.

| | Disk | RAM (CPU / float32) | VRAM (GPU / float16) |
|---|---|---|---|
| Florence-2-base-ft | ~445 MB | ~1 GB | ~0.5 GB |
| BioCLIP v2 | ~1.6 GB | ~3.2 GB | ~1.6 GB |
| **Total** | **~2 GB** | **~4-5 GB** | **~2-3 GB** |

On CPU, models use `float32` (4 bytes per parameter), so RAM usage is roughly 2x the disk size. On GPU with `float16`, VRAM usage is closer to the disk size. Add ~0.5-1 GB overhead for PyTorch, the FastAPI server, and image processing during inference.

**Minimum recommended**: 8 GB RAM (CPU) or 4 GB VRAM (GPU).

### Startup

On startup, both models are loaded into memory. The first few requests to each endpoint will be slower than steady state (~2-3x) due to PyTorch's lazy kernel initialization. Performance stabilizes after 2-3 requests.

### Temp files

BioCLIP's classifier expects a file path, not raw image data. Each BioCLIP request writes the decoded image to a temporary file in `/tmp/` which is **not** automatically cleaned up. On long-running servers, these temp files will accumulate. Consider adding periodic cleanup or a tmpwatch/cron job.

### Why is inference slow?

Both models run on CPU by default (`float32`). On a CUDA GPU they use `float16` and are significantly faster. Florence is especially slow on CPU because it's a generative model that decodes tokens one at a time.

### Florence tasks

Florence-2 supports multiple vision tasks via a task prompt:

- `<CAPTION>` - short caption (default)
- `<DETAILED_CAPTION>` - longer description
- `<MORE_DETAILED_CAPTION>` - most verbose
- `<OD>` - object detection with bounding boxes
- `<DENSE_REGION_CAPTION>` - captions per region
- `<OCR>` - text recognition
- `<OCR_WITH_REGION>` - text with bounding boxes

**Note:** Florence produces generic captions (e.g. "an animal in water"), not species-level identification. Use BioCLIP for that.

### BioCLIP ranks

BioCLIP classifies images at any taxonomic rank:

`kingdom`, `phylum`, `class`, `order`, `family`, `genus`, `species`

Omitting the `ranks` field returns all 7 ranks. BioCLIP v2 covers 952K taxa.

To use the smaller BioCLIP v1 (~600 MB, 450K taxa), edit `inference/bioclip.py`:

```python
from bioclip import BIOCLIP_V1_MODEL_STR
classifier = TreeOfLifeClassifier(model_str=BIOCLIP_V1_MODEL_STR)
```

## Requirements

- Python 3.12+
- CUDA-capable GPU (optional, falls back to CPU)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For CPU-only PyTorch installations:

```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

On first run, models are downloaded and cached to `.huggingface/models/`. Subsequent runs load from cache.

## Running

```bash
python main.py
```

The server starts on `http://localhost:8000`. API docs are available at `http://localhost:8000/docs`.

## API Endpoints

### POST /florence

Generate a caption or run a vision task on an image.

**Request:**
```json
{
  "image_b64": "<base64 encoded image>",
  "task": "<CAPTION>"
}
```

**Response:**
```json
{
  "<CAPTION>": "A couple of animals that are standing in the water."
}
```

### POST /bioclip

Classify an image at one or more taxonomic ranks.

**Request:**
```json
{
  "image_b64": "<base64 encoded image>",
  "ranks": ["kingdom", "family", "species"]
}
```

Omit `ranks` to get all 7 ranks.

**Response:**
```json
{
  "kingdom": [
    {"kingdom": "Animalia", "score": 0.9993},
    ...
  ],
  "species": [
    {"species": "Hydrochoeris hydrochaeris", "common_name": "Capybara", "score": 0.40},
    ...
  ]
}
```

## Project Structure

```
main.py                  # FastAPI application
inference/
  __init__.py            # Shared config (HF_HOME)
  florence.py            # Florence-2-base-ft model
  bioclip.py             # BioCLIP v2 classifier
requirements.txt         # Pinned dependencies
```
