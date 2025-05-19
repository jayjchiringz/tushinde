import uuid
from sqlalchemy.orm import Session
from . import models, database
from fastapi import APIRouter, Request, Depends # type: ignore
from fastapi.responses import PlainTextResponse # type: ignore

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_ussd_steps(text: str) -> list[str]:
    return text.strip().split("*") if text else []


def generate_entry_code() -> str:
    return str(uuid.uuid4()).split("-")[0].upper()


@router.post("/ussd/entry")
async def ussd_entry(request: Request, db: Session = Depends(get_db)):
    print("[🛰️ AT CALLBACK RECEIVED]")
    try:
        form = await request.form()
        session_id = form.get("sessionId")
        phone = form.get("phoneNumber")
        text = form.get("text", "")

        print(f"[📥 USSD] New request received — SessionID: {session_id}, Phone: {phone}")
        print("[📨 FORM DATA]", dict(form))
    except Exception as e:
        print(f"[❌ FORM ERROR] {e}")
        return PlainTextResponse("END Error reading request.")

    session_id = form.get("sessionId")
    phone = form.get("phoneNumber")
    text = form.get("text", "")

    steps = parse_ussd_steps(text)
    level = len(steps)

    if level == 0:
        return PlainTextResponse("CON Welcome to Tushinde\n1. Daily\n2. Weekly")

    if level == 1:
        if steps[0] not in ["1", "2"]:
            return PlainTextResponse("END Invalid choice. Please dial again.")
        return PlainTextResponse("CON Enter amount (e.g. 50):")

    if level == 2:
        game_type = "daily" if steps[0] == "1" else "weekly"
        try:
            amount = float(steps[1])
        except ValueError:
            return PlainTextResponse("END Invalid amount. Please dial again.")

        entry_code = generate_entry_code()

        ticket = models.Ticket(
            phone=phone,
            game_type=game_type,
            amount=amount,
            entry_code=entry_code,
            confirmed=False
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        print(f"[🎟️ TICKET CREATED] {entry_code} for {phone} - {game_type} KES {amount}")
        return PlainTextResponse(f"END Ticket {entry_code} created.\nYou’ll receive a payment prompt shortly.")

    return PlainTextResponse("END Invalid navigation. Please dial again.")
