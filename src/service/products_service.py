from dataclasses import dataclass
from uuid import UUID
import json

from src.models import Products
from src.repository.products_repository import ProductsRepository
from src.schemas.products import ProductResponse


@dataclass
class ProductsService:
    products_repository: ProductsRepository

    async def get_all(self) -> list[ProductResponse]:
        products = await self.products_repository.get_all_products()
        return [self._prepare_product_response(product) for product in products]

    async def get_by_id(self, product_id: UUID) -> Products:
        product = await self.products_repository.get_by_id(product_id)
        return self._prepare_product_response(product) if product else None
        
    def _prepare_product_response(self, product: Products) -> ProductResponse:
        """Transform the database Product model to ProductResponse schema"""
        product_dict = {
            column.key: getattr(product, column.key)
            for column in product.__table__.columns
        }
        
        # Десериализуем features из JSON-строки в список
        if product.features and isinstance(product.features, str):
            try:
                # Пытаемся распарсить строку как JSON
                product_dict['features'] = json.loads(product.features)
                
                # Проверяем, не нужно ли сделать дополнительную обработку Unicode
                if product_dict['features'] and isinstance(product_dict['features'][0], str):
                    # Если строки выглядят как экранированные Unicode, разэкранируем их
                    if '\\u' in product_dict['features'][0]:
                        product_dict['features'] = [
                            feature.encode('utf-8').decode('unicode_escape') 
                            for feature in product_dict['features']
                        ]
            except json.JSONDecodeError:
                # Если не получается распарсить JSON, возвращаем пустой список
                product_dict['features'] = []
        
        return ProductResponse.model_validate(product_dict)
