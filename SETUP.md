# MindMapAI - 설정 및 사용 가이드

## 프로젝트 소개

주제를 입력하면 Gemini AI가 계층적 마인드맵을 자동으로 생성하고, 노드 확장 및 협업 기능을 제공하는 서비스입니다.

---

## 필요한 API 키 / 환경변수 목록

| 변수명 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 | https://aistudio.google.com/app/apikey |
| `SECRET_KEY` | JWT 서명용 비밀 키 | 직접 생성 (예: `openssl rand -hex 32`) |
| `PORTONE_SECRET_KEY` | 포트원(아임포트) 결제 시크릿 키 | https://admin.portone.io |
| `PORTONE_IMP_KEY` | 포트원(아임포트) 가맹점 식별코드 | https://admin.portone.io |
| `DATABASE_URL` | 데이터베이스 연결 URL (기본: SQLite) | - |
| `FREE_DAILY_LIMIT` | 무료 플랜 일일 생성 횟수 (기본: 5) | - |

---

## GitHub Secrets 설정 방법

저장소 페이지 > **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

| Secret 이름 | 값 |
|---|---|
| `GEMINI_API_KEY` | Google AI Studio에서 발급한 키 |
| `SECRET_KEY` | 프로덕션용 JWT 비밀 키 |
| `PORTONE_SECRET_KEY` | 포트원 시크릿 키 |
| `PORTONE_IMP_KEY` | 포트원 가맹점 식별코드 |

---

## 로컬 개발 환경 설정

### 1. `.env` 파일 생성

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./mindmapai.db
PORTONE_SECRET_KEY=your_portone_secret_key
PORTONE_IMP_KEY=your_portone_imp_key
FREE_DAILY_LIMIT=5
DEBUG=false
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

---

## 실행 방법

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버 실행 후 http://localhost:8000/docs 에서 Swagger UI를 확인할 수 있습니다.

### Docker로 실행

```bash
docker-compose up --build
```

---

## API 엔드포인트 주요 사용법

### 헬스 체크

```
GET /health
```

### 회원가입

```
POST /api/users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword",
  "full_name": "홍길동"
}
```

### 로그인 (JWT 토큰 발급)

```
POST /api/users/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

응답으로 받은 `access_token`을 이후 요청의 `Authorization: Bearer <token>` 헤더에 포함합니다.

### 마인드맵 생성

```
POST /api/mindmaps/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "topic": "인공지능의 미래",
  "depth": 3
}
```

응답에 계층 구조 `root_node`(JSON 트리)가 포함됩니다.

### 마인드맵 목록 조회

```
GET /api/mindmaps/
Authorization: Bearer <access_token>
```

### 마인드맵 상세 조회

```
GET /api/mindmaps/{mindmap_id}
Authorization: Bearer <access_token>
```

### 노드 확장 (특정 노드 하위 항목 AI 생성)

```
POST /api/mindmaps/{mindmap_id}/expand
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "node_id": "node_uuid",
  "node_text": "머신러닝"
}
```

### 마인드맵 수정 (공개/비공개, 제목 변경)

```
PATCH /api/mindmaps/{mindmap_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "새 제목",
  "is_public": true
}
```

### 결제 검증 (포트원)

```
POST /api/payments/verify
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "imp_uid": "imp_xxxxxxxxxx",
  "merchant_uid": "order_xxxxxxxxxx",
  "amount": 9900
}
```

---

전체 API 문서: http://localhost:8000/docs
