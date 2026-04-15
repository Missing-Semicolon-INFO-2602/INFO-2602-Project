# Description

Hello! This is a Pokedex made for capturing real life animals, created by the group Missing Semicolon.

Our lightweight Vision Language Model, BioCLIP, will tell you what species it is. (P.S.: the server pre-loads the model and warms up Torch kernels during startup for the best user experience.)

Get started using the following steps:

- Create your user account or log in
- Snap a picture
- Upload it on the Scan Animal page
- See it in My Collection (with your own photo) and on your personal Animal Map!

You can also browse our animal database, which is seeded from the iNaturalist and GBIF APIs. If you catch an animal that's not in the database yet, we'll look it up and add it for you.

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

- **BioCLIP v2** (Imageomics) — taxonomic classification at species rank

## Model

| Model / Data          | Size    | Purpose                                                                 | Notes                                 |
| --------------------- | ------- | ----------------------------------------------------------------------- | ------------------------------------- |
| BioCLIP v2 (ViT-L/14) | ~1.6 GB | Species classification                                                  | Downloaded automatically on first run |
| TreeOfLife-200M       | ~2.6 GB | Taxonomy labels and precomputed text embeddings for BioCLIP's 952K taxa | Downloaded automatically on first run |

### Memory requirements

The model is loaded into RAM at startup and stays resident for the lifetime of the server.

|            | Disk      | RAM (CPU / float32) | VRAM (GPU / float16) |
| ---------- | --------- | ------------------- | -------------------- |
| BioCLIP v2 | ~1.6 GB   | ~3.2 GB             | ~1.6 GB              |
| **Total**  | **~2 GB** | **~4-5 GB**         | **~2-3 GB**          |

On CPU, the model uses `float32` (4 bytes per parameter), so RAM usage is roughly 2x the disk size. On GPU with `float16`, VRAM usage is closer to the disk size. Add ~0.5-1 GB overhead for PyTorch, the FastAPI server, and image processing during inference.

**Minimum recommended**: 8 GB RAM (CPU) or 4 GB VRAM (GPU).

### Startup

On startup the model is loaded and a warmup inference runs so Torch kernels are compiled before the first real request. After that, steady-state latency kicks in immediately. The classifier automatically uses the GPU when CUDA is available and falls back to CPU otherwise.

### Why is CPU inference slow?

The model runs on CPU with `float32` when no GPU is available. On a CUDA GPU it uses `float16` and is significantly faster. Scanimal only asks for the top species prediction (`k=1`) per request to keep work to a minimum.

### Swapping BioCLIP versions

To use the smaller BioCLIP v1 (~600 MB, 450K taxa), edit `app/inference/bioclip.py`:

```python
from bioclip import BIOCLIP_V1_MODEL_STR
classifier = TreeOfLifeClassifier(model_str=BIOCLIP_V1_MODEL_STR, device=_device)
```

## Requirements

- Python 3.12+
- CUDA-capable GPU (optional, falls back to CPU)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
cp env.example .env
```

For CPU-only PyTorch installations:

```bash
pip install . --extra-index-url https://download.pytorch.org/whl/cpu
```

The `.env` file is read by `app/config.py` via `pydantic-settings`. The defaults (SQLite, `ENV=development`) are fine for local dev.

On first run, models are downloaded and cached to `.huggingface/models/`. Subsequent runs load from cache.

## Running

Development server (reload on file changes):

```bash
fastapi dev main.py
```

Alternatively:

```bash
python main.py          # or
python -m main          # or
uvicorn main:app        # no reload
```

The server starts on `http://localhost:8000`. API docs are available at `http://localhost:8000/docs`.

### Demo accounts

The app seeds demo users on first boot. Sign in at `/login` with any of these (password is always `1234`):

| Username | Role  |
| -------- | ----- |
| bob      | admin |
| john     | user  |
| alice    | user  |
| charlie  | user  |

### Pages

| Path           | What it does                                                                 |
| -------------- | ---------------------------------------------------------------------------- |
| `/`            | Redirects to `/app` (home) when logged in, otherwise to `/login`             |
| `/app`         | Home dashboard with the nav cards                                            |
| `/results`     | Drag / drop an image to scan an animal                                       |
| `/collection`  | Your personal gallery plus a radial tree of species you've caught            |
| `/database`    | Browse and search the full animal catalog (iNaturalist + GBIF seeded)        |
| `/leaderboard` | Ranked list of users by distinct species caught this week                    |
| `/friends`     | Friends page                                                                 |
| `/admin`       | Admin-only page (bob's role)                                                 |
| `/docs`        | FastAPI interactive OpenAPI docs                                             |

## API endpoints

### POST `/bioclip`

Classify an image. Requires an authenticated session (`access_token` cookie is set by `POST /login`). Returns the top species prediction and links it to the current user's collection.

**Request:**

```json
{
  "image_b64": "<base64 encoded image, no data: prefix>"
}
```

**Response:**

```json
{
  "species": "Panthera leo",
  "common_name": "Lion",
  "pic": "https://inaturalist-open-data.s3.amazonaws.com/photos/.../square.jpg"
}
```

### GET `/api/animals/tree`

Returns the taxonomy hierarchy of the current user's collected species as nested JSON (suitable for D3's `hierarchy` / `tree` layouts). Requires an authenticated session.

**Response:**

```json
{
  "name": "Life",
  "children": [
    {
      "name": "Animalia",
      "children": [
        { "name": "Chordata", "children": [ ... ] }
      ]
    }
  ]
}
```

### GET `/api/users`

Returns the list of users as JSON.
