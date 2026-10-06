from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="Sample Python App", version="1.0.0")
_INDEX_PATH = Path(__file__).parent / "templates" / "index.html"


@app.get("/")
def read_root() -> FileResponse:
    return FileResponse(_INDEX_PATH)


@app.get("/api/status")
def read_status() -> dict[str, str]:
    return {"message": "Hello from Python on AKS", "status": "running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}