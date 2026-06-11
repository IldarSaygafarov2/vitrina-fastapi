from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from backend.api import router as api_router
from backend.app.config import config
from backend.app.dependencies import get_repo
from infrastructure.database.repo.requests import RequestsRepo
from config.constants import REPAIR_TYPE_MAPPING

main_app = FastAPI(debug=True)
main_app.include_router(api_router)

main_app.mount("/static", StaticFiles(directory="backend/static"), name="static")
main_app.mount("/media", StaticFiles(directory="media"), name="media")


templates = Jinja2Templates(directory="backend/templates")


main_app.add_middleware(
    SessionMiddleware,
    secret_key=config.secret_key,
    max_age=86400,
)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@main_app.get("/", response_class=HTMLResponse)
async def show_home_page(
    request: Request, repo: Annotated[RequestsRepo, Depends(get_repo)]
):
    categories = await repo.categories.get_categories()
    districts = await repo.districts.get_districts()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "home page",
            "categories": categories,
            "districts": districts,
            "repair_types": REPAIR_TYPE_MAPPING,
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=config.run_api.api_host,
        port=config.run_api.api_port,
        reload=True,
    )
