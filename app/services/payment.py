"""포트원(PortOne) 결제 서비스 스켈레톤"""
import httpx
from app.config import config

PORTONE_API_BASE = "https://api.iamport.kr"


async def get_portone_token() -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PORTONE_API_BASE}/users/getToken",
            json={"imp_key": config.PORTONE_IMP_KEY, "imp_secret": config.PORTONE_SECRET_KEY},
        )
        resp.raise_for_status()
        return resp.json()["response"]["access_token"]


async def verify_payment(imp_uid: str) -> dict:
    token = await get_portone_token()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PORTONE_API_BASE}/payments/{imp_uid}",
            headers={"Authorization": token},
        )
        resp.raise_for_status()
        return resp.json()["response"]
