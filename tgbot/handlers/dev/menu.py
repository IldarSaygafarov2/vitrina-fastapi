from aiogram import Router, types, F
from aiogram.filters import CommandStart

from infrastructure.database.repo.requests import RequestsRepo

dev_router = Router()
