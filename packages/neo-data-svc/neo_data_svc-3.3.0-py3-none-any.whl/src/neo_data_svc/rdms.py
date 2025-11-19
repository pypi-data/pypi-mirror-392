import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import Column, DateTime, func, text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlmodel import Field, SQLModel, select

from .common import NDS_get_v

_executor = ThreadPoolExecutor(10)


class NDPModel(SQLModel):
    __abstract__ = True


T = TypeVar("T")
M = TypeVar("M", bound=NDPModel)
_url = NDS_get_v("DB")
assert _url is not None

async_engine = create_async_engine(
    f"postgresql+asyncpg://{_url}", echo=False, future=True)
async_AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def NDP_add_task(*k):
    return await asyncio.get_running_loop().run_in_executor(_executor, *k)


async def NDP_init_db():
    assert async_engine is not None
    async with async_engine.begin() as c:
        await c.run_sync(NDPModel.metadata.create_all)


async def NDP_get_db():
    assert async_AsyncSessionLocal is not None
    async with async_AsyncSessionLocal() as s:
        yield s


async def NDP_get(
    db: AsyncSession,
    model: Type[M],
    **filters
):
    stmt = select(model).filter_by(**filters)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def NDP_all(
    db: AsyncSession,
    model: Type[M],
    **filters
):
    stmt = select(model).filter_by(**filters)
    result = await db.execute(stmt)
    return result.scalars().all()


async def NDP_add(
        db: AsyncSession,
        model: Type[M],
        **kwargs
):
    obj = model(**kwargs)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def NDP_patch(
    db: AsyncSession,
    instance: M,
    **kwargs
) -> M:
    for k, v in kwargs.items():
        setattr(instance, k, v)
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    return instance


async def NDP_delete(
    db: AsyncSession,
    instance: M
) -> M | None:
    await db.delete(instance)
    await db.commit()
