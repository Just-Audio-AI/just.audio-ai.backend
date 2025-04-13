from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api import routers


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["*"],
)
for router in routers:
    app.include_router(router)
