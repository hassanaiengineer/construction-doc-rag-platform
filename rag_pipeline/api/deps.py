from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from rag_pipeline.core.config import Settings
from rag_pipeline.core.paths import StoragePaths


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_paths(request: Request) -> StoragePaths:
    return request.app.state.paths


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session
