from fastapi import APIRouter, Query, HTTPException, Depends # type: ignore
from sqlalchemy.orm import Session
from . import notifier, database, models

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sms/status")
def sms_delivery_status(unique_id: str = Query(...)):
    result = notifier.check_delivery_status(unique_id)
    return result

@router.get("/sms/status/by-entry")
def sms_status_by_entry(code: str = Query(...), db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.entry_code == code).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not ticket.sms_id:
        raise HTTPException(status_code=400, detail="No SMS sent for this ticket")

    return notifier.check_delivery_status(ticket.sms_id)
