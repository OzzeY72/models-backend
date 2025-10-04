from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import WorkUser
import random

from schemas import RegisterRequest, VerifyRequest

router = APIRouter(prefix="/auth", tags=["auth"])

def send_otp_via_whatsapp(phonenumber: str, otp: str):
    # Здесь должна быть реализация отправки OTP через WhatsApp API
    print(f"Sending OTP {otp} to phone number {phonenumber} via WhatsApp")

@router.post("/register")
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    otp = str(111111) # str(random.randint(100000, 999999))

    user = db.query(WorkUser).filter_by(telegram_id=data.telegram_id).first()
    if not user:
        user = WorkUser(telegram_id=data.telegram_id, phonenumber=data.phonenumber, otp_code=otp)
        db.add(user)
    else:
        user.otp_code = otp
        user.verified = False

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
    return {"message": "Verified successfully"}
