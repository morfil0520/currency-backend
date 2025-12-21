from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.currency import CurrencyRate
from app.api.schemas import ItemCreate, ItemUpdate, ItemResponse
from app.nats.client import nats_client

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/", response_model=list[ItemResponse])
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CurrencyRate))
    return result.scalars().all()

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CurrencyRate).where(CurrencyRate.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

@router.post("/", response_model=ItemResponse)
async def create_item(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db)
):
    item = CurrencyRate(**data.dict())
    db.add(item)
    await db.commit()
    await db.refresh(item)

    await nats_client.publish(
        "items.updates",
        {
            "event": "item_created",
            "id": item.id,
            "char_code": item.char_code,
        }
    )

    return item

@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    data: ItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CurrencyRate).where(CurrencyRate.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)

    await nats_client.publish(
        "items.updates",
        {
            "event": "item_updated",
            "id": item.id,
        }
    )

    return item

@router.delete("/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CurrencyRate).where(CurrencyRate.id == item_id)
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()

    await nats_client.publish(
        "items.updates",
        {
            "event": "item_deleted",
            "id": item_id,
        }
    )

    return {"status": "deleted"}