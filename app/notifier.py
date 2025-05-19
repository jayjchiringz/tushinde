import os
import requests
import logging
from dotenv import load_dotenv # type: ignore

load_dotenv()

API_URL = "http://167.172.14.50:4002/v1/send-sms"
API_CLIENT_ID = "731"
API_KEY = "h5Q3pYYcYbQm5Wj"
API_SECRET = "ok4m5RWdoHOWhUEeDyARjIyTHKbqvy"
SERVICE_ID = "1"


def send_sms(phone: str, message: str):
    if phone.startswith("07"):
        phone = "254" + phone[1:]
    elif phone.startswith("+254"):
        phone = phone[1:]

    sanitized_message = ''.join(c for c in message if ord(c) < 128)

    form_data = {
        "apiClientID": API_CLIENT_ID,
        "key": API_KEY,
        "txtMessage": sanitized_message,
        "MSISDN": phone,
        "serviceID": SERVICE_ID
    }

    try:
        print("[📤 DEBUG] Sending SMS with payload:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")

        response = requests.post(API_URL, files=form_data)

        print(f"[📥 DEBUG] HTTP Status: {response.status_code}")
        print(f"[📥 DEBUG] Raw response: {response.text!r}")

        if not response.text.strip():
            print("[⚠️ EMPTY RESPONSE] No JSON returned — assuming delivery")
            return "unknown"  # 🟢 CRITICAL LINE

        try:
            data = response.json()
            if data.get("status") == 222:
                unique_id = str(data.get("unique_id"))
                print(f"[✅ SMS SENT] {phone} | ID: {unique_id}")
                return unique_id
            else:
                print(f"[⚠️ SMS ERROR] {phone} | Status: {data.get('status')} | Message: {data.get('status_message')}")
                return "unknown"  # 🟢 fallback

        except Exception as e:
            print(f"[⚠️ JSON PARSE FAILED] {e}")
            return "unknown"  # 🟢 fallback

    except Exception as e:
        print(f"[❌ SMS FAILED] {phone}: {e}")
        return None  # only return None if request fails entirely


def check_delivery_status(unique_id: str):
    REPORT_URL = "https://app.bongasms.co.ke/api/fetch-delivery"

    params = {
        "apiClientID": API_CLIENT_ID,
        "key": API_KEY,
        "unique_id": unique_id
    }

    try:
        print(f"[📡 CHECKING DELIVERY] ID: {unique_id}")
        response = requests.get(REPORT_URL, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"[📬 DELIVERY STATUS] {data}")
        return data
    except Exception as e:
        print(f"[❌ DELIVERY CHECK FAILED] {e}")
        return {"error": str(e)}
