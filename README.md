# MindMapAI

AI가 주제를 입력받아 마인드맵을 자동 생성하고 협업까지 지원하는 서비스입니다.

## 주요 기능

- 주제 입력 → Gemini AI로 마인드맵 트리 구조 자동 생성
- 마인드맵 저장 / 편집 / 삭제
- 공유 링크로 협업 (공개/비공개 전환)
- 노드 확장 (특정 노드의 하위 항목 추가 생성)
- PDF/PNG 내보내기 메타데이터 제공
- JWT 인증 + 프리미엄 플랜 (무료: 하루 5회)

## 기술 스택

- **Backend**: FastAPI, SQLAlchemy async, aiosqlite
- **AI**: Google Gemini API
- **결제**: PortOne (아임포트)
- **인증**: JWT

## 시작하기

```bash
cp .env.example .env
# .env에 API 키 입력

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## Docker

```bash
docker-compose up --build
```

## API 문서

서버 실행 후 http://localhost:8001/docs 접속

## 플랜

| 기능 | 무료 | 프리미엄 |
|------|------|----------|
| 하루 생성 횟수 | 5회 | 무제한 |
| 마인드맵 저장 | O | O |
| 공유 링크 | O | O |
| 노드 확장 | O | O |
