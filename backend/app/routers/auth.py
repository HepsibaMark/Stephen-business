from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import generate_otp, send_otp_email, otp_expiry, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-otp", response_model=schemas.RequestOTPOut)
def request_otp(payload: schemas.RequestOTP, db: Session = Depends(get_db)):
    """Step 1 of login: generate and email an OTP for this address.
    TEST MODE (no email credentials configured): the code is printed to
    the backend console AND returned in the response so you can test
    without setting up email sending yet."""
    code = generate_otp()
    otp_row = models.OTPCode(
        email=payload.email,
        code=code,
        expires_at=otp_expiry(),
    )
    db.add(otp_row)
    db.commit()

    real_email_sent = send_otp_email(payload.email, code)

    return schemas.RequestOTPOut(
        message=f"OTP sent to {payload.email}",
        debug_otp=None if real_email_sent else code,
    )


@router.post("/verify-otp", response_model=schemas.TokenOut)
def verify_otp(payload: schemas.VerifyOTP, db: Session = Depends(get_db)):
    """Step 2 of login: check the OTP, create the user profile if this is
    their first login, and return a JWT access token."""
    otp_row = (
        db.query(models.OTPCode)
        .filter(
            models.OTPCode.email == payload.email,
            models.OTPCode.code == payload.code,
            models.OTPCode.is_used == False,  # noqa: E712
        )
        .order_by(models.OTPCode.created_at.desc())
        .first()
    )

    if not otp_row:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    expires_at = otp_row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired — request a new one")

    otp_row.is_used = True
    db.commit()

    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        user = models.User(
            name=payload.name or "Customer",
            email=payload.email,
            phone=payload.phone,
            role=models.UserRole.customer,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})
    return schemas.TokenOut(access_token=token, user=user)
