"""
Auth helpers: OTP generation/verification and JWT tokens.

TEST MODE vs REAL EMAIL
------------------------
If EMAIL_ADDRESS and EMAIL_APP_PASSWORD are NOT set in your .env file,
send_otp_email() falls back to TEST MODE — it just prints the code to
the console instead of sending a real email. This is what you've been
using so far, completely free, no setup needed.

To send REAL emails (still free, using your own Gmail account):
1. Turn on 2-Step Verification on your Google account (Google Account
   settings -> Security -> 2-Step Verification).
2. Create an "App Password": Google Account -> Security -> App
   Passwords -> generate one for "Mail". Google gives you a 16-character
   password — this is NOT your normal Gmail password.
3. In your .env file, set:
     EMAIL_ADDRESS=youraddress@gmail.com
     EMAIL_APP_PASSWORD=the16characterapppassword
4. Restart the backend. That's it — no other code changes needed.
   send_otp_email() below automatically switches to real sending once
   these two variables are present.
"""

import os
import random
import smtplib
import string
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
OTP_EXPIRE_MINUTES = 5

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def send_otp_email(to_email: str, code: str) -> bool:
    """Sends the OTP by email. Returns True if a real email was sent,
    False if it fell back to test mode (so the caller knows whether to
    include the code in the API response)."""
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        print(f"[TEST MODE] OTP for {to_email}: {code}")
        return False

    msg = MIMEText(
        f"Your Grocery Delivery login code is: {code}\n\n"
        f"This code expires in {OTP_EXPIRE_MINUTES} minutes."
    )
    msg["Subject"] = "Your login code"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[EMAIL SEND FAILED, falling back to test mode] {e}")
        print(f"[TEST MODE] OTP for {to_email}: {code}")
        return False


def otp_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None
