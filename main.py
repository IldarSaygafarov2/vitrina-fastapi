import uvicorn
from fastapi import FastAPI

from backend.api import router as api_router

main_app = FastAPI()

main_app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(
        "main:main_app",
        host='127.0.0.1',
        port=8000,
        reload=True,
    )
