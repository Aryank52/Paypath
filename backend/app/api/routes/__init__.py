from app.api.routes.auth import router as auth_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.paycore import router as paycore_router
from app.api.routes.intent import router as intent_router
from app.api.routes.shop import router as shop_router
from app.api.routes.guard import router as guard_router
from app.api.routes.reclaim import router as reclaim_router
from app.api.routes.recover import router as recover_router
from app.api.routes.policies import router as policies_router
from app.api.routes.agents import router as agents_router
from app.api.routes.audit import router as audit_router

__all__ = [
    "auth_router",
    "transactions_router",
    "paycore_router",
    "intent_router",
    "shop_router",
    "guard_router",
    "reclaim_router",
    "recover_router",
    "policies_router",
    "agents_router",
    "audit_router"
]
