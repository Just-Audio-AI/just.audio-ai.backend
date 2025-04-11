from fastapi import APIRouter, Depends

from src.dependency import get_products_service
from src.schemas.products import Products as ProductsSchema
from src.service.products_service import ProductsService

router = APIRouter(
    tags=["products"],
    prefix="/products",
)


@router.get(
    "/active",
    response_model=list[ProductsSchema],
)
async def get_all_products(
    products_service: ProductsService = Depends(get_products_service),
):
    products = await products_service.get_all()
    return products
