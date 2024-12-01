from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.interfaces.consultation import ConsultationCreateDTO, ConsultationDTO
from infrastructure.database.repo.requests import RequestsRepo

router = APIRouter(
    prefix=config.api_prefix.v1.consultation,
    tags=['Consultation']
)


@router.post('/create')
async def create_consultation(
        consultation_data: ConsultationCreateDTO,
        repo: Annotated[RequestsRepo, Depends(get_repo)]
):
    new = await repo.consultation.create(
        fullname=consultation_data.fullname,
        phone_number=consultation_data.phone_number
    )
    return ConsultationDTO.model_validate(new, from_attributes=True)
