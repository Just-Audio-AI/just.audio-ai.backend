from src.api.audio_convert import router as audio_convert_router
from src.api.auth import router as auth_router

routers = [value for name, value in globals().items() if name.endswith("_router") and callable(value)]
