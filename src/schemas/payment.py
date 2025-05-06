from pydantic import BaseModel


class CloudPaymentsRecurrentCallback(BaseModel):
    Id: str
    Amount: float  # Сумма операции
    AccountId: str  # ID пользователя
    Status: str  # Статус операции: Authorized, Completed, Declined
    Interval: str
