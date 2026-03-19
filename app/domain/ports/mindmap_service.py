from abc import abstractmethod
from typing import Any, Dict, List, Optional
from app.domain.ports.base_service import AbstractService


class AbstractMindMapService(AbstractService):
    @abstractmethod
    async def create_map(self, user_id: int, title: str, source_text: str) -> Dict[str, Any]: ...
    @abstractmethod
    async def generate_nodes(self, map_id: int, parent_node_id: Optional[int] = None) -> List[Dict[str, Any]]: ...
    @abstractmethod
    async def export_map(self, map_id: int, format: str = "json") -> Dict[str, Any]: ...
