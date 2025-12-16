from fastapi import FastAPI

app = FastAPI(title="Secure Multi-Tenant Backend")

@app.get("/health")
def health_check():
    return {"status": "ok"}
