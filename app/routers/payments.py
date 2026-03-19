from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.payment import Payment
from app.utils.auth import get_current_user
from app.services import payment as payment_service

router = APIRouter(prefix="/api/payments", tags=["payments"])


class PaymentVerifyRequest(BaseModel):
    imp_uid: str
    merchant_uid: str
    amount: float


@router.post("/verify")
async def verify_payment(
    body: PaymentVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        payment_data = await payment_service.verify_payment(body.imp_uid)
    except Exception:
        raise HTTPException(status_code=502, detail="결제 검증 서버 연결 실패")

    if payment_data.get("amount") != body.amount:
        raise HTTPException(status_code=400, detail="결제 금액이 일치하지 않습니다.")
    if payment_data.get("status") != "paid":
        raise HTTPException(status_code=400, detail="결제가 완료되지 않았습니다.")

    payment = Payment(
        user_id=current_user.id,
        imp_uid=body.imp_uid,
        merchant_uid=body.merchant_uid,
        amount=body.amount,
        status="paid",
    )
    db.add(payment)
    current_user.is_premium = True
    await db.commit()
    return {"message": "프리미엄 플랜이 활성화되었습니다.", "is_premium": True}


@router.get("/history")
async def payment_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Payment).where(Payment.user_id == current_user.id))
    payments = result.scalars().all()
    return [
        {"id": p.id, "imp_uid": p.imp_uid, "amount": p.amount, "status": p.status, "created_at": p.created_at}
        for p in payments
    ]
