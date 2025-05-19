from fastapi import FastAPI # type: ignore
from . import ussd, payment, draw, delivery
from .database import Base, engine
from .models import Ticket, DrawEvent

Base.metadata.create_all(bind=engine)
print("[🛠️ DB INIT] Tables created")

app = FastAPI()
app.include_router(ussd.router)
app.include_router(payment.router)
app.include_router(draw.router)
app.include_router(delivery.router)
