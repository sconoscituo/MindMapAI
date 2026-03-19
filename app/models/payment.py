from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    imp_uid = Column(String, unique=True, nullable=False)
    merchant_uid = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, paid, failed, cancelled
    plan = Column(String, default="premium_monthly")
    created_at = Column(DateTime, server_default=func.now())
