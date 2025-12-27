import httpx
import xml.etree.ElementTree as ET
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.currency import CurrencyRate

CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"

class CurrencyService:

    @staticmethod
    async def fetch_from_cbr() -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(CBR_URL)
            response.raise_for_status()

        root = ET.fromstring(response.text)
        rate_date = root.attrib.get("Date")

        result = []

        for valute in root.findall("Valute"):
            result.append({
                "char_code": valute.findtext("CharCode"),
                "name": valute.findtext("Name"),
                "nominal": int(valute.findtext("Nominal")),
                "value": float(valute.findtext("Value").replace(",", ".")),
                "date": rate_date
            })

        return result

    @staticmethod
    async def save_to_db(session: AsyncSession, rates: list[dict]):

        await session.execute(text("DELETE FROM currency_rates"))

        for r in rates:
            session.add(CurrencyRate(**r))

        await session.commit()
