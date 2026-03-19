from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.mindmap import MindMap
from app.utils.auth import get_current_user
from app.services.generator import generate_mindmap, expand_node, _count_nodes
from app.config import config

router = APIRouter(prefix="/api/mindmaps", tags=["mindmaps"])


class MindMapCreate(BaseModel):
    topic: str
    depth: int = 3


class MindMapUpdate(BaseModel):
    title: Optional[str] = None
    root_node: Optional[dict] = None
    is_public: Optional[bool] = None


class MindMapOut(BaseModel):
    id: int
    title: str
    topic: str
    root_node: dict
    is_public: bool
    share_token: Optional[str]
    depth: int
    node_count: int

    class Config:
        from_attributes = True


class NodeExpand(BaseModel):
    node_text: str


def check_daily_limit(user: User):
    today = str(date.today())
    if user.last_usage_date != today:
        user.daily_usage = 0
        user.last_usage_date = today
    if not user.is_premium and user.daily_usage >= config.FREE_DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"무료 플랜은 하루 {config.FREE_DAILY_LIMIT}회까지 가능합니다. 프리미엄으로 업그레이드하세요.",
        )


@router.post("/generate", response_model=MindMapOut, status_code=status.HTTP_201_CREATED)
async def generate(
    body: MindMapCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_daily_limit(current_user)

    root_node = await generate_mindmap(body.topic, body.depth)
    node_count = _count_nodes(root_node)

    mindmap = MindMap(
        user_id=current_user.id,
        title=body.topic,
        topic=body.topic,
        root_node=root_node,
        depth=body.depth,
        node_count=node_count,
    )
    db.add(mindmap)
    current_user.daily_usage += 1
    await db.commit()
    await db.refresh(mindmap)
    return mindmap


@router.get("/", response_model=list[MindMapOut])
async def list_mindmaps(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MindMap).where(MindMap.user_id == current_user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/shared/{share_token}", response_model=MindMapOut)
async def get_shared(share_token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MindMap).where(MindMap.share_token == share_token, MindMap.is_public == True)
    )
    mindmap = result.scalar_one_or_none()
    if not mindmap:
        raise HTTPException(status_code=404, detail="공유된 마인드맵을 찾을 수 없습니다.")
    return mindmap


@router.get("/{mindmap_id}", response_model=MindMapOut)
async def get_mindmap(
    mindmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MindMap).where(MindMap.id == mindmap_id, MindMap.user_id == current_user.id)
    )
    mindmap = result.scalar_one_or_none()
    if not mindmap:
        raise HTTPException(status_code=404, detail="마인드맵을 찾을 수 없습니다.")
    return mindmap


@router.patch("/{mindmap_id}", response_model=MindMapOut)
async def update_mindmap(
    mindmap_id: int,
    body: MindMapUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MindMap).where(MindMap.id == mindmap_id, MindMap.user_id == current_user.id)
    )
    mindmap = result.scalar_one_or_none()
    if not mindmap:
        raise HTTPException(status_code=404, detail="마인드맵을 찾을 수 없습니다.")

    if body.title is not None:
        mindmap.title = body.title
    if body.root_node is not None:
        mindmap.root_node = body.root_node
        mindmap.node_count = _count_nodes(body.root_node)
    if body.is_public is not None:
        mindmap.is_public = body.is_public

    await db.commit()
    await db.refresh(mindmap)
    return mindmap


@router.post("/{mindmap_id}/share")
async def share_mindmap(
    mindmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MindMap).where(MindMap.id == mindmap_id, MindMap.user_id == current_user.id)
    )
    mindmap = result.scalar_one_or_none()
    if not mindmap:
        raise HTTPException(status_code=404, detail="마인드맵을 찾을 수 없습니다.")

    if not mindmap.share_token:
        mindmap.share_token = MindMap.generate_share_token()
    mindmap.is_public = True
    await db.commit()

    return {"share_token": mindmap.share_token, "share_url": f"/api/mindmaps/shared/{mindmap.share_token}"}


@router.post("/{mindmap_id}/unshare")
async def unshare_mindmap(
    mindmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MindMap).where(MindMap.id == mindmap_id, MindMap.user_id == current_user.id)
    )
    mindmap = result.scalar_one_or_none()
    if not mindmap:
        raise HTTPException(status_code=404, detail="마인드맵을 찾을 수 없습니다.")

    mindmap.is_public = False
    await db.commit()
    return {"message": "공유가 해제되었습니다."}


@router.post("/{mindmap_id}/expand")
async def expand_mindmap_node(
    mindmap_id: int,
    body: NodeExpand,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MindMap).where(MindMap.id == mindmap_id, MindMap.user_id == current_user.id)
    )
    mindmap = result.scalar_one_or_none()
    if not mindmap:
        raise HTTPException(status_code=404, detail="마인드맵을 찾을 수 없습니다.")

    children = await expand_node(body.node_text, mindmap.topic)
    return {"node_text": body.node_text, "children": children}


@router.delete("/{mindmap_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mindmap(
    mindmap_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MindMap).where(MindMap.id == mindmap_id, MindMap.user_id == current_user.id)
    )
    mindmap = result.scalar_one_or_none()
    if not mindmap:
        raise HTTPException(status_code=404, detail="마인드맵을 찾을 수 없습니다.")
    await db.delete(mindmap)
    await db.commit()


@router.get("/{mindmap_id}/export")
async def export_mindmap(
    mindmap_id: int,
    format: str = "json",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MindMap).where(MindMap.id == mindmap_id, MindMap.user_id == current_user.id)
    )
    mindmap = result.scalar_one_or_none()
    if not mindmap:
        raise HTTPException(status_code=404, detail="마인드맵을 찾을 수 없습니다.")

    return {
        "format": format,
        "title": mindmap.title,
        "topic": mindmap.topic,
        "root_node": mindmap.root_node,
        "node_count": mindmap.node_count,
        "export_hint": f"프론트엔드에서 {format.upper()} 렌더링 후 다운로드하세요.",
    }
