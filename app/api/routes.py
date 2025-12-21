from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.currency import CurrencyRate
from sqlalchemy import select

router = APIRouter(prefix="/rates", tags=["CBR"])

@router.get("/")
async def get_all_rates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CurrencyRate))
    return result.scalars().all()


@router.get("/{code}")
async def get_rate(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CurrencyRate).where(CurrencyRate.char_code == code.upper())
    )
    rate = result.scalar_one_or_none()

    if not rate:
        return {"error": "Currency not found"}

    return rate