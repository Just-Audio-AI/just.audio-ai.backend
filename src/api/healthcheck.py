from fastapi import APIRouter


router = APIRouter(
    tags=["healthcheck"],
    prefix="/healthcheck",
)


@router.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
