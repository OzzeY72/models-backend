from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from middleware import create_access_token, get_current_user, verify_token
from models import WorkUser
import random

from schemas import RegisterRequest, VerifyRequest

router = APIRouter(prefix="/auth", tags=["auth"])

def send_otp_via_whatsapp(phonenumber: str, otp: str):
    # Здесь должна быть реализация отправки OTP через WhatsApp API
    print(f"Sending OTP {otp} to phone number {phonenumber} via WhatsApp")

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(WorkUser).filter_by(telegram_id=current_user["telegram_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "telegram_id": user.telegram_id,
        "phonenumber": user.phonenumber,
        "user_type": user.user_type,
        "linked_profile_id": str(user.linked_profile_id) if user.linked_profile_id else None,
        "verified": user.verified,
    }

@router.post("/register")
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    otp = str(111111) # str(random.randint(100000, 999999))

    user = db.query(WorkUser).filter_by(telegram_id=data.telegram_id).first()
    if not user:
        user = WorkUser(telegram_id=data.telegram_id, phonenumber=data.phonenumber, otp_code=otp)
        db.add(user)
    else:
        user.otp_code = otp

    db.commit()

    # Отправляем через WhatsApp API
    send_otp_via_whatsapp(data.phonenumber, otp)

    return {"message": "OTP sent via WhatsApp"}

@router.post("/verify")
def verify_user(data: VerifyRequest, db: Session = Depends(get_db)):
    user = db.query(WorkUser).filter_by(telegram_id=data.telegram_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    if user.otp_code != data.code:
        raise HTTPException(400, "Invalid code")

    user.verified = True
    db.commit()

    access_token = create_access_token(
        data={"telegram_id": user.telegram_id, "phonenumber": user.phonenumber},
        expires_delta=timedelta(hours=1)
    )

    return {
        "message": "Verified successfully",
        "token": access_token,
        "user": {
            "telegram_id": user.telegram_id,
            "phonenumber": user.phonenumber,
            "user_type": user.user_type,
            "linked_profile_id": str(user.linked_profile_id) if user.linked_profile_id else None,
        },
    }