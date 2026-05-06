from __future__ import annotations

from fastapi import APIRouter

from construction_rag.api.schemas.admin import HealthOut

router = APIRouter()


@router.get("/health", response_model=HealthOut)
async def health() -> HealthOut:
    return HealthOut(status="ok")

