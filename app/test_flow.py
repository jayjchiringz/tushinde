# Simulated test for full flow

import requests

BASE = "http://127.0.0.1:8000"

def full_flow():
    # Step 1: Enter via USSD
    res1 = requests.post(BASE + "/ussd/entry", json={
        "phone": "0707123456",
        "game_type": "Daily Jackpot",
        "amount": 50
    })
    print("USSD Entry:", res1.json())
    entry_code = res1.json()["entry_code"]

    # Step 2: Mock Payment
    res2 = requests.post(BASE + "/payment/mock-confirm", json={
        "entry_code": entry_code
    })
    print("Payment:", res2.json())

    # Step 3: Draw Now
    res3 = requests.post(BASE + "/draw-now", headers={
        "x-api-key": "secret-tushinde-key"
    })
    print("Draw Result:", res3.json())

full_flow()
