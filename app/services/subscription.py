from enum import Enum
class PlanType(str, Enum):
    FREE = "free"; PRO = "pro"  # 월 5,900원
PLAN_LIMITS = {
    PlanType.FREE: {"mindmaps": 5,  "ai_generate": 3,  "share_link": False, "export": False},
    PlanType.PRO:  {"mindmaps": 100,"ai_generate": 50, "share_link": True,  "export": True},
}
PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 5900}
