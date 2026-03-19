import secrets
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, DateTime, func
from app.database import Base


class MindMap(Base):
    __tablename__ = "mindmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    root_node = Column(JSON, nullable=False)   # full tree JSON
    is_public = Column(Boolean, default=False)
    share_token = Column(String, unique=True, index=True, nullable=True)
    depth = Column(Integer, default=3)
    node_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @staticmethod
    def generate_share_token() -> str:
        return secrets.token_urlsafe(16)
