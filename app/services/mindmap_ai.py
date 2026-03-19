import json
import re
import google.generativeai as genai
from app.config import config


def _build_text_tree(node: dict, prefix: str = "", is_last: bool = True) -> str:
    """마인드맵 트리를 텍스트 형식으로 변환 (재귀)"""
    connector = "└── " if is_last else "├── "
    line = prefix + (connector if prefix else "") + node.get("text", "")
    lines = [line]

    children = node.get("children", [])
    for i, child in enumerate(children):
        extension = "    " if is_last else "│   "
        child_prefix = prefix + (extension if prefix else "")
        lines.append(_build_text_tree(child, child_prefix, i == len(children) - 1))

    return "\n".join(lines)


class MindMapAIService:
    """
    Gemini AI 기반 마인드맵 자동 생성 및 확장 서비스
    - 노드 자동 확장
    - 전체 마인드맵 구조 생성 (루트 → 1단계 → 2단계)
    - 노드 간 연관성 분석
    - JSON / 텍스트 내보내기
    """

    def __init__(self):
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def expand_node(
        self,
        node_text: str,
        depth: int = 1,
        count: int = 5,
    ) -> list:
        """
        노드 텍스트로부터 하위 아이디어 자동 생성
        - node_text: 확장할 노드의 텍스트
        - depth: 현재 트리 깊이 (프롬프트 맥락 제공용)
        - count: 생성할 하위 노드 수
        """
        if not self.model:
            return self._fallback_expand(node_text, count)

        prompt = f"""
마인드맵 노드: "{node_text}"
이 노드에서 파생될 수 있는 하위 아이디어 {count}개를 생성해줘.
각 아이디어는 10자 이내로 간결하게.
반드시 JSON 배열만 출력: ["아이디어1", "아이디어2", ...]
한국어로 작성.
"""
        try:
            response = await self.model.generate_content_async(prompt)
            match = re.search(r'\[.*?\]', response.text, re.DOTALL)
            if match:
                ideas = json.loads(match.group())
                return [
                    {"id": f"exp-{i+1}", "text": str(idea)[:20], "children": []}
                    for i, idea in enumerate(ideas[:count])
                ]
        except Exception:
            pass
        return self._fallback_expand(node_text, count)

    async def generate_full_mindmap(self, topic: str, depth: int = 2) -> dict:
        """
        주제로부터 전체 마인드맵 구조 생성
        구조: 루트 → 1단계 5개 → 2단계 각 3개
        """
        if not self.model:
            return self._fallback_full_mindmap(topic)

        prompt = f"""주제 "{topic}"에 대한 마인드맵을 생성하세요.
구조: 루트(1개) → 1단계 핵심 주제(5개) → 2단계 세부 항목(각 3개)
각 노드 텍스트는 15자 이내로 간결하게.
반드시 아래 JSON 형식만 출력하세요 (다른 텍스트 없이):
{{"id":"root","text":"{topic}","children":[
  {{"id":"1","text":"핵심주제1","children":[
    {{"id":"1-1","text":"세부항목1","children":[]}},
    {{"id":"1-2","text":"세부항목2","children":[]}},
    {{"id":"1-3","text":"세부항목3","children":[]}}
  ]}}
]}}
한국어로 작성."""

        try:
            response = await self.model.generate_content_async(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                tree = json.loads(match.group())
                return tree
        except Exception:
            pass
        return self._fallback_full_mindmap(topic)

    async def suggest_connections(self, nodes: list) -> list:
        """
        노드 간 연관성 분석 및 연결 제안
        - nodes: 노드 텍스트 목록
        - 반환: [{"from": "노드A", "to": "노드B", "reason": "연관 이유"}, ...]
        """
        if not self.model or not nodes:
            return []

        nodes_text = ", ".join(f'"{n}"' for n in nodes[:20])
        prompt = f"""다음 마인드맵 노드들 사이의 연관성을 분석하고 연결을 제안하세요.
노드 목록: [{nodes_text}]

서로 연관성이 높은 노드 쌍을 최대 5개 찾아 JSON 배열로 반환하세요:
[{{"from": "노드A", "to": "노드B", "reason": "연관 이유 (15자 이내)"}}]
한국어로 작성. 반드시 JSON 배열만 출력."""

        try:
            response = await self.model.generate_content_async(prompt)
            match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if match:
                connections = json.loads(match.group())
                return connections[:5]
        except Exception:
            pass
        return []

    def export_json(self, mindmap_data: dict) -> dict:
        """
        마인드맵을 JSON 형식으로 내보내기
        - 완전한 트리 구조 + 메타데이터 포함
        """
        return {
            "format": "json",
            "version": "1.0",
            "title": mindmap_data.get("title", ""),
            "topic": mindmap_data.get("topic", ""),
            "node_count": mindmap_data.get("node_count", 0),
            "depth": mindmap_data.get("depth", 3),
            "root_node": mindmap_data.get("root_node", {}),
            "metadata": {
                "created_at": str(mindmap_data.get("created_at", "")),
                "exported_format": "json",
            },
        }

    def export_text(self, mindmap_data: dict) -> dict:
        """
        마인드맵을 텍스트 트리 형식으로 내보내기
        - 터미널 트리 스타일 (├── / └── 사용)
        """
        root_node = mindmap_data.get("root_node", {})
        text_tree = _build_text_tree(root_node)

        return {
            "format": "text",
            "title": mindmap_data.get("title", ""),
            "topic": mindmap_data.get("topic", ""),
            "node_count": mindmap_data.get("node_count", 0),
            "content": text_tree,
            "metadata": {
                "created_at": str(mindmap_data.get("created_at", "")),
                "exported_format": "text",
            },
        }

    # ── 폴백 (AI 키 미설정 시) ──────────────────────────────────

    def _fallback_expand(self, node_text: str, count: int) -> list:
        return [
            {"id": f"exp-{i+1}", "text": f"{node_text} 항목{i+1}", "children": []}
            for i in range(count)
        ]

    def _fallback_full_mindmap(self, topic: str) -> dict:
        branches = ["개요", "핵심 개념", "응용 사례", "장단점", "발전 방향"]
        return {
            "id": "root",
            "text": topic,
            "children": [
                {
                    "id": str(i + 1),
                    "text": branch,
                    "children": [
                        {"id": f"{i+1}-{j+1}", "text": f"{branch} {j+1}", "children": []}
                        for j in range(3)
                    ],
                }
                for i, branch in enumerate(branches)
            ],
        }


# 전역 인스턴스
mindmap_ai = MindMapAIService()
