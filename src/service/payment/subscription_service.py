from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from src.models.products import UserProducts
from src.repository.user_products_repository import UserProductsRepository
from src.settings import Settings


@dataclass
class SubscriptionService:
    user_products_repository: UserProductsRepository
    settings: Settings
