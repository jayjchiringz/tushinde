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
    pool = db.query(models.Ticket).filter(
        models.Ticket.confirmed == True,
        models.Ticket.is_winner == False
    ).all()

    print(f"\n[🎯 DRAW INITIATED] {len(pool)} eligible entries")

    if not pool:
        print("[⚠️ NO ENTRIES FOUND] Creating fallback test ticket...")
        fallback = models.Ticket(
            phone="254700000001",
            game_type="daily",
            amount=50,
            entry_code=str(random.randint(10000000, 99999999)),
            confirmed=True
        )
        db.add(fallback)
        db.commit()
        db.refresh(fallback)
        pool = [fallback]

    print("[🔄 SHUFFLING ENTRIES]")
    random.shuffle(pool)

    print("[⏱️ COUNTDOWN] Preparing to draw...")
    for i in range(3, 0, -1):
        print(f"🎬 Drawing in {i}...")
        time.sleep(1)

    winner = random.choice(pool)
    winner.is_winner = True
    db.commit()

    print(f"\n🏆 WINNER SELECTED")
    print(f"📱 {winner.phone}")
    print(f"🎟️ Code: {winner.entry_code}")

    message = (
        f"🎉 Congratulations!\n"
        f"You've won the Tushinde draw.\n"
        f"Entry Code: {winner.entry_code}\n"
        f"Check tushinde.com for prize details!"
    )

    sms_id = notifier.send_sms(winner.phone, message)
    winner.sms_id = sms_id or "unknown"
    db.commit()

    print(f"[📩 SMS DISPATCHED] ID: {winner.sms_id}")

    # 💾 Log draw event
    draw_event = models.DrawEvent(
        ticket_id=winner.id,
        phone=winner.phone,
        entry_code=winner.entry_code,
        sms_id=winner.sms_id
    )
    db.add(draw_event)
    db.commit()

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

    return [
        {
            "entry_code": d.entry_code,
            "phone": d.phone,
            "sms_id": d.sms_id,
            "draw_time": d.draw_time,
            "payout_status": d.payout_status
        }
        for d in draw_logs
    ]
