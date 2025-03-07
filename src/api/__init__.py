from src.api.audio_convert import router as audio_convert_router
from src.api.auth.email import router as email_auth_router
from src.api.auth.firebase import router as firebase_auth_router
from src.api.products import router as products_router

routers = [value for name, value in globals().items() if name.endswith("_router") and callable(value)]
