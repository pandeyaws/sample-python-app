from fastapi import FastAPI

app = FastAPI(title="Sample Python App", version="1.0.0")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from Python on AKS", "status": "running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}