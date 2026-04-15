# Description

Hello! This is a Pokedex made for capturing real life animals, created by the group Missing Semicolon.

Our lightweight Vision Language Model, BioClip, will tell you what species it is. (P.S.: Running the init() funcition will pre-load them into memory for the best user experience.)

Get started using the following steps:

- Create your user account or log in
- Snap a picture
- Upload it
- See them in your gallery!

You can also browse our animal wiki which uses iNaturalist and GBIF APIs to show you the most popular species. If you find an animal that's not there, you can upload the image and we'll add it for you!

## What is the Model View Controller (MVC) pattern?

The MVC pattern is a code pattern that is used to organise the modules of a project and when applied to a project, it usually works as follows:

- **Models** are your SQLModel/SQLAlchemy classes (The classes that become database tables)
- **Controllers** are utility functions used to mutate models and/or perform business logic
- **Views** bind controllers to http routes passing along any user parameters from the request to the controller

## What is the Service repository pattern?

The Service Repository pattern is designed to keep business logic separate from the data access and it aims to separate the codebase into distinct layers.

- **The Repository Layer** acts as a mediator between the application and the data source (the database, files, etc)
- **The Service Layer** sits between the controller and the repository and this is where business logic lives.

The job of the **repository layer** is to handle **_CRUD_** operations on a model. It doesn't care about the rules at the business logic layer, it's only concerned about how to get and manipulate data.

The job of the **service layer** is to handle the **RULES** of the application. This is where the business logic comes in such as checking to see if a user's authorized to access the data.

# Scanimal

A FastAPI application for animal/species identification using a vision language model:

- **BioCLIP v2** (Imageomics) - taxonomic classification at any rank

## Models

| Model / Data          | Size    | Purpose                                                                 | Speed (CPU)                           |
| --------------------- | ------- | ----------------------------------------------------------------------- | ------------------------------------- |
| BioCLIP v2 (ViT-L/14) | ~1.6 GB | Species/taxonomy classification                                         | ~9s (all 7 ranks)                     |
| TreeOfLife-200M       | ~2.6 GB | Taxonomy labels and precomputed text embeddings for BioCLIP's 952K taxa | Downloaded automatically on first run |

### Memory requirements

The model is loaded into RAM at startup and stay resident for the lifetime of the server.

|            | Disk      | RAM (CPU / float32) | VRAM (GPU / float16) |
| ---------- | --------- | ------------------- | -------------------- |
| BioCLIP v2 | ~1.6 GB   | ~3.2 GB             | ~1.6 GB              |
| **Total**  | **~2 GB** | **~4-5 GB**         | **~2-3 GB**          |

On CPU, the model uses `float32` (4 bytes per parameter), so RAM usage is roughly 2x the disk size. On GPU with `float16`, VRAM usage is closer to the disk size. Add ~0.5-1 GB overhead for PyTorch, the FastAPI server, and image processing during inference.

**Minimum recommended**: 8 GB RAM (CPU) or 4 GB VRAM (GPU).

### Startup

On startup, the model is loaded into memory. The first few requests to each endpoint will be slower than steady state (~2-3x) due to PyTorch's lazy kernel initialization. Performance stabilizes after 2-3 requests.

### Temp files

BioCLIP's classifier expects a file path, not raw image data. Each BioCLIP request writes the decoded image to a temporary file in `/tmp/` which is **not** automatically cleaned up. On long-running servers, these temp files will accumulate. Consider adding periodic cleanup or a tmpwatch/cron job.

### Why is inference slow?

Both models run on CPU by default (`float32`). On a CUDA GPU they use `float16` and are significantly faster. Florence is especially slow on CPU because it's a generative model that decodes tokens one at a time.

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
pip install .
```

For CPU-only PyTorch installations:

```bash
pip install . --extra-index-url https://download.pytorch.org/whl/cpu
```

On first run, models are downloaded and cached to `.huggingface/models/`. Subsequent runs load from cache.

## Running

```bash
python main.py
```

The server starts on `http://localhost:8000`. API docs are available at `http://localhost:8000/docs`.

## API Endpoints

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
