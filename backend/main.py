from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import os
import shutil
import hashlib

from analyzer import analyze_image


app = FastAPI(
    title="DeepGuard AI API",
    description="AI-powered digital media authenticity detection"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@app.get("/")
def home():
    return {
        "message": "DeepGuard AI Backend Running"
    }


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


@app.post("/analyze")
async def analyze_media(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    sha256_hash = calculate_sha256(
        file_path
    )

    result = analyze_image(
        file_path
    )

    result["sha256"] = sha256_hash

    return {
        "filename": file.filename,
        "status": "analysis_complete",
        "result": result
    }