import json
import re
import google.generativeai as genai
from app.config import config

genai.configure(api_key=config.GEMINI_API_KEY)


def _count_nodes(node: dict) -> int:
    """트리 노드 수 재귀 계산"""
    count = 1
    for child in node.get("children", []):
        count += _count_nodes(child)
    return count


async def generate_mindmap(topic: str, depth: int = 3) -> dict:
    """주제로 마인드맵 트리 구조 생성"""
    if not config.GEMINI_API_KEY:
        return {
            "id": "root",
            "text": topic,
            "children": [
                {
                    "id": "1",
                    "text": f"{topic} 핵심 개념",
                    "children": [
                        {"id": "1-1", "text": "세부 항목 1", "children": []},
                        {"id": "1-2", "text": "세부 항목 2", "children": []},
                    ],
                },
                {
                    "id": "2",
                    "text": f"{topic} 응용",
                    "children": [
                        {"id": "2-1", "text": "응용 사례 1", "children": []},
                        {"id": "2-2", "text": "응용 사례 2", "children": []},
                    ],
                },
            ],
        }

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""주제 "{topic}"에 대한 마인드맵을 JSON 트리로 생성하세요. 깊이는 {depth}입니다.
반드시 아래 JSON 형식만 출력하세요:
{{"id":"root","text":"{topic}","children":[{{"id":"1","text":"핵심개념1","children":[{{"id":"1-1","text":"세부항목","children":[]}}]}}]}}
한국어로 작성하고, 각 노드의 children은 3-5개로 구성하세요."""

    response = model.generate_content(prompt)
    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"id": "root", "text": topic, "children": []}


async def expand_node(node_text: str, parent_topic: str) -> list[dict]:
    """특정 노드를 확장하여 자식 노드 생성"""
    if not config.GEMINI_API_KEY:
        return [
            {"id": f"exp-{i}", "text": f"{node_text} 하위항목 {i}", "children": []}
            for i in range(1, 4)
        ]

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""마인드맵에서 "{parent_topic}" 주제의 "{node_text}" 노드를 확장합니다.
하위 항목 4개를 JSON 배열로 생성하세요:
[{{"id":"1","text":"하위항목1","children":[]}},{{"id":"2","text":"하위항목2","children":[]}}]
한국어로 작성하세요."""

    response = model.generate_content(prompt)
    match = re.search(r'\[.*\]', response.text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return []
