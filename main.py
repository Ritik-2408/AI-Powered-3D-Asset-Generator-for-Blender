import os
import uuid
import traceback

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import pollinations_client
import triposr_runner

app = FastAPI()

OUTPUTS_ROOT = "outputs"


class GenerateRequest(BaseModel):
    prompt: str


@app.on_event("startup")
def startup_event():
    # Load TripoSR ONCE when the server starts, not per-request.
    triposr_runner.load_model()


@app.post("/generate-3d")
def generate_3d(req: GenerateRequest):
    job_id = str(uuid.uuid4())[:8]
    job_dir = os.path.join(OUTPUTS_ROOT, job_id)
    os.makedirs(job_dir, exist_ok=True)

    try:
        image_path = pollinations_client.fetch_image(req.prompt, job_dir)
    except RuntimeError as e:
        return JSONResponse(status_code=502, content={"error": f"2D generation failed: {e}"})

    try:
        obj_path = triposr_runner.generate_mesh(image_path, job_dir)
    except RuntimeError as e:
        return JSONResponse(status_code=500, content={"error": f"3D reconstruction failed: {e}"})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Unexpected error: {e}"})

    return FileResponse(obj_path, media_type="application/octet-stream", filename="mesh.obj")