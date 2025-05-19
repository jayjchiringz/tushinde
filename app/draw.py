import os
import time
import random

from fastapi import APIRouter, Depends, Header, HTTPException # type: ignore
from sqlalchemy.orm import Session
from . import models, notifier, database

router = APIRouter()
API_KEY = os.getenv("ADMIN_API_KEY")


# ---------------------------
# 🔧 Dependencies
# ---------------------------

def get_db():
    
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


# ---------------------------
# 🎯 Draw Execution
# ---------------------------

@router.post("/draw-now", dependencies=[Depends(check_api_key)])
def draw_now(db: Session = Depends(get_db)):
    # 🧩 Step 1: Get all eligible tickets
    pool = db.query(models.Ticket).filter(
        models.Ticket.confirmed == True,
        models.Ticket.is_winner == False
    ).all()

    print(f"\n[🎯 DRAW INITIATED] Eligible entries found: {len(pool)}")

    if not pool:
        raise HTTPException(
            status_code=400,
            detail="No eligible tickets found. Make sure users have entered and confirmed payment."
        )

    # 🔄 Step 2: Shuffle and pick winner
    random.shuffle(pool)
    winner = random.choice(pool)
    winner.is_winner = True
    db.commit()

    print(f"\n🏆 WINNER SELECTED")
    print(f"📱 {winner.phone}")
    print(f"🎟️ Code: {winner.entry_code}")

    # 📩 Step 3: Send winner SMS
    message = (
        f"🎉 Congratulations!\n"
        f"You've won the Tushinde draw.\n"
        f"Entry Code: {winner.entry_code}\n"
        f"Draw Date: {winner.created_at.strftime('%d-%b-%Y')}\n"
        f"Visit tushinde.com for prize info."
    )

    sms_id = notifier.send_sms(winner.phone, message)
    winner.sms_id = sms_id or "unknown"
    db.commit()

    print(f"[📩 SMS DISPATCHED] ID: {winner.sms_id}")

    # 🧾 Step 4: Log draw event
    draw_event = models.DrawEvent(
        ticket_id=winner.id,
        phone=winner.phone,
        entry_code=winner.entry_code,
        sms_id=winner.sms_id,
        payout_status="pending"
    )
    db.add(draw_event)
    db.commit()
    print(f"[💾 DRAW EVENT SAVED] ID: {draw_event.id}")

    return {
        "message": "Draw completed successfully.",
        "winner": {
            "phone": winner.phone,
            "entry": winner.entry_code
        }
    }


@router.get("/draw/history", dependencies=[Depends(check_api_key)])
def get_draw_history(db: Session = Depends(get_db)):
    draw_logs = db.query(models.DrawEvent).order_by(models.DrawEvent.draw_time.desc()).limit(10).all()

    print(f"[🔍 HISTORY] Found {len(draw_logs)} events")
    for d in draw_logs:
        print(f" ↪️ {d.entry_code} | {d.phone} | {d.draw_time}")

    return [
        {
            "entry_code": d.entry_code,
            "phone": d.phone,
            "sms_id": d.sms_id,
            "draw_time": str(d.draw_time),
            "payout_status": d.payout_status
        }
        for d in draw_logs
    ]


@router.get("/debug/tickets")
def get_tickets(db: Session = Depends(get_db)):
    return [
        {
            "entry_code": t.entry_code,
            "confirmed": t.confirmed,
            "phone": t.phone,
            "created_at": str(t.created_at),
            "is_winner": t.is_winner,
            "sms_id": t.sms_id
        }
        for t in db.query(models.Ticket).order_by(models.Ticket.created_at.desc()).limit(10).all()
    ]
