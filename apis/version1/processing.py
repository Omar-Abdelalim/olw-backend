from http.client import HTTPException

from fastapi import APIRouter, Depends, Header, Request, Body, Response, status, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.session import get_db
from typing import Annotated
import json
import bcrypt
import random
from random import randrange
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from pydantic import BaseModel

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db.models.account import Account
from db.models.customer import Customer
from db.models.kyc import KYC
from db.models.otp import OTP
from db.models.notification import Notification
from db.models.password import Password
from db.models.transaction import Transaction
from db.models.sms import Sms
from db.models.exTransaction import TransactionRequest
from db.models.inTransaction import TransactionRequestIncoming
from db.models.fees import Fee
from db.models.bank import Bank
from db.models.currency import Currency
from db.models.bankBusiness import BankBusiness
from db.models.options import Options
from db.models.bioToken import Biometric
from db.models.qr import QR
from db.models.qrTerminal import QRTer
from db.models.charge import Charge
from db.models.card import Card
from db.models.vcards import VCard
from db.models.vcard_status_log import VCardLogs

from db.globals.global_variables import tokens
from apis.version1.encyption import decrypt, encrypt, DecryptRequest, decrypt_data

import requests
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from core.hashing import Hasher

router = APIRouter()

numberOfOPTTrials = 3
countryCodes = {"Egypt": "+20", "USA": "+1", "KSA": "+966"}  # Example list of allowed countries
OTPvalidMinutes = 10
OTPLength = 4

origins = [

    "http://localhost",
    "http://localhost:8080",
]


def encode(body):
    return body


def decode(body):
    return body


def log(filename, line):
    try:
        with open('../logs/' + filename + ".txt", 'a+') as file:
            file.write(line + '\n')
        return True
    except Exception as e:
        print("An error occurred:", str(e))
        return False


def decrypt_message_again(data: DecryptRequest):
    from fastapi.responses import JSONResponse
    try:
        if not data.message:
            raise HTTPException(status_code=400, detail="encrypted_data field is required")
        decrypted_message = decrypt_data(data.message).decode()
    except HTTPException as e:
        print(e.datils)
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Unexpected error: {str(e)}"})
    plaintext2_str = decrypted_message

    print(type(plaintext2_str))

    return plaintext2_str


def preprocess(data: DecryptRequest, names, requ):
    p = json.loads(data.message)

    print("from ",requ," :", p)

    # p = p.replace("'", '\"')
    # p = json.loads(p)
    l = log("requests", "time: " + str(datetime.now()) + " api: " + requ + " body: " + str(p))
    if not l:
        return {"status_code": 301, "message": "error logging request"}
    for i in names:
        if i not in p:
            return {"status_code": 400, "message": "missing variable: " + i}
    return {"status_code": 200, "message": "payload edited", "payload": p}


def generateOTP(length):
    return "".join(random.choice('0123456789') for _ in range(length))


def generate_bank_account(customerID, account_type=1, sub_account=1, currency_code=1):
    last_account_number = int(customerID) + 100

    account_type_str = f"{int(account_type):02}"
    sub_account_str = f"{int(sub_account):03}"
    currency_code_str = f"{int(currency_code):02}"

    account_number_str = f"{last_account_number:08}"
    bank_account = f"{account_type_str}-{account_number_str}-{sub_account_str}-{currency_code_str}"

    return bank_account


class DecryptRequest(BaseModel):
    message: str


@router.post("/login")
async def signIn(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
  try:
    em = payload["email"]

    pa = payload["password"]
    code = payload["code"]
    print(em)
    print(pa)
    print(code)
    hashed_password = pa.encode('utf-8')


    user = db.query(Customer).filter(Customer.email == em).first()

    if not user:
        return {"status_code": 403, "message": "no user exists with this email"}
    if not user.smsCode == code:
        print(user.smsCode)
        return {"status_code": 404, "message": "wrong code"}
    elif datetime.now() > datetime.strptime(user.smsValid, '%Y-%m-%d %H:%M:%S.%f'):
        return {"status_code": 404, "message": "code timed- out"}


    password = db.query(Password).filter(Password.customerID == str(user.id) , Password.passwordStatus == "active").first()

    if not Hasher.verify_password(hashed_password, password.passwordHash):
        return {"status_code": 404, "message": "Password doesn't match email", "orig": hashed_password,
                "other": password}
    db.query(Token).filter(Token.customerID == user.id).update({"status": "expired"})
    t = Token(customerID=str(user.id), dateTime=datetime.now(), ip=request.client.host, token=generateToken(user.id),
              expiration=datetime.now() + timedelta(minutes=tokenValidMins), status="active",deviceID="none")
    db.add(t)
    db.commit()
    db.refresh(t)
    account = db.query(Account).filter(Account.customerID == str(user.id), Account.primaryAccount == "1").first()
    bank = db.query(Bank).filter(Bank.accountNumber == account.accountNumber).first()
    bankb = db.query(BankBusiness).filter(BankBusiness.accountNumber == account.accountNumber).first()
    
    

  except:
         message = "exception occurred with retrieving token"
         log(0,message)
         return {"status_code":401,"message":message}
  return {"status_code":200,"user":user,"token":t,"account":account,"bank":bank,"bankBusiness":bankb}