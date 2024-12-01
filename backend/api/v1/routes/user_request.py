from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.interfaces.user_request import UserRequestDTO, UserRequestCreateDTO
from infrastructure.database.repo.requests import RequestsRepo

router = APIRouter(
    prefix=config.api_prefix.v1.request,
    tags=['Users requests']
)


@router.post('/add')
async def add_user_request(
        request_data: UserRequestCreateDTO,
        repo: Annotated[RequestsRepo, Depends(get_repo)]
) -> UserRequestDTO:
    new_request = await repo.user_request.create(
        first_name=request_data.first_name,
        phone_number=request_data.phone_number,
        operation_type=request_data.operation_type,
        object_type=request_data.object_type,
        message=request_data.message,
    )
    return UserRequestDTO.model_validate(new_request, from_attributes=True)
