import uvicorn
from fastapi import FastAPI

from backend.api import router as api_router
from backend.app.config import config
from fastapi.staticfiles import StaticFiles
main_app = FastAPI()
main_app.include_router(api_router)

main_app.mount("/media", StaticFiles(directory="media"), name="media")

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=config.run_api.api_host,
        port=config.run_api.api_port,
        reload=True,
    )
