from fastapi import FastAPI
import logging
from starlette.middleware.cors import CORSMiddleware

from src.api import routers
import sentry_sdk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

sentry_sdk.init(
    dsn="https://35cabfeff5fe1553ef06c42187d691ad@o4509270271393792.ingest.de.sentry.io/4509270274867280",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

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
