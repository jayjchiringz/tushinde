from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy.orm import Session
from . import models, schemas, notifier, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/payment/mock-confirm")
def mock_payment(data: schemas.PaymentConfirm, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.entry_code == data.entry_code).first()
    if not ticket:
        print(f"[❌ PAYMENT ERROR] No ticket found for code {data.entry_code}")
        return {"error": "Invalid code"}

    # ✅ Move this line out of unreachable code
    ticket.confirmed = True

    sms_id = notifier.send_sms(ticket.phone, f"Payment received! Your ticket {ticket.entry_code} is entered.")
    ticket.sms_id = sms_id or "unknown"
    db.commit()
    print(f"[💾 SMS ID SAVED] {ticket.entry_code} → {ticket.sms_id}")
    return {"message": "Payment confirmed"}
