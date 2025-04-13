from fastapi import APIRouter, Depends, status

from src.dependency import get_products_service
from src.schemas.products import ProductResponse
from src.service.products_service import ProductsService

router = APIRouter(
    tags=["products"],
    prefix="/products",
)


@router.get(
    "/active",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all active products",
    description="""
    Retrieve all active products available for purchase.
    
    Returns:
    - List of products with their prices, features and current discounts
    - Each product contains information about available minutes for audio transcription
    - If a product has an active discount, it will include discounted price and deadline
    """,
    response_description="List of available products"
)
async def get_all_products(
    products_service: ProductsService = Depends(get_products_service),
) -> list[ProductResponse]:
    """
    Get all active products with their current prices and discounts.
    
    Args:
        products_service: Service for product operations
        
    Returns:
        List[ProductResponse]: List of available products
    """
    return await products_service.get_all()
