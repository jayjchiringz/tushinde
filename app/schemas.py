from pydantic import BaseModel # type: ignore

class EntryRequest(BaseModel):
    phone: str
    game_type: str
    amount: float

class PaymentConfirm(BaseModel):
    entry_code: str
