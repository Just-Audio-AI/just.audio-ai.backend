from src.api.audio_convert import (
    router as audio_convert_router,  # noqa: F403 F401
)
from src.api.auth.email import router as email_auth_router  # noqa: F403 F401
from src.api.auth.firebase import router as firebase_auth_router  # noqa: F403 F401
from src.api.chat import router as chat_router  # noqa: F403 F401
from src.api.products import router as products_router  # noqa: F403 F401
from src.api.user_files import router as user_files_router  # noqa: F403 F401
from src.api.users.user import router as user_router  # noqa: F403 F401
from src.api.payment.payments import router as payments_router  # noqa: F403 F401
from src.api.payment.user_payment import (
    router as user_payment_router,  # noqa: F403 F401
)
from src.api.healthcheck import router as healthcheck_router  # noqa: F403 F401

routers = [
    value
    for name, value in globals().items()
    if name.endswith("_router") and callable(value)
]
