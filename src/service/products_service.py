from src.models import Products
from src.repository.products_repository import ProductsRepository
from dataclasses import dataclass


@dataclass
class ProductsService:
    products_repository: ProductsRepository

    async def get_all(self) -> list[Products]:
        return await self.products_repository.get_all_products()
