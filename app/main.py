from fastapi import FastAPI
from app.config import settings

app = FastAPI()

@app.get("/")

def read_root():
    return {
        "message":"Hello World",
            "environment": settings.environment,
        }

@app.get("/health")
def health_check():
   return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }

 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)