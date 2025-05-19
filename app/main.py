from fastapi import FastAPI # type: ignore
from . import ussd, payment, draw, delivery
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(ussd.router)
app.include_router(payment.router)
app.include_router(draw.router)
app.include_router(delivery.router)
