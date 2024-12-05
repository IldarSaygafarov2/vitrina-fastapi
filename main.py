import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.api import router as api_router
from backend.app.config import config

main_app = FastAPI()
main_app.include_router(api_router)

main_app.mount("/media", StaticFiles(directory="media"), name="media")


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://ivitrina-nedvizhimosti.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=config.run_api.api_host,
        port=config.run_api.api_port,
        reload=True,
    )
