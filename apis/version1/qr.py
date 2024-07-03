from http.client import HTTPException

from fastapi import APIRouter, Depends, Header, Request, Body, Response, status, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

import pandas as pd
import string
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

from db.globals.global_variables import tokens,session_exp_time
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


def preprocess(data: DecryptRequest, names, requ,ip):
    p = json.loads(data.message)

    print("from ",requ," :", p)

    # p = p.replace("'", '\"')
    # p = json.loads(p)
    l = log("requests", "time: " + str(datetime.now()) + " api: " + requ + " body: " + str(p))
    if not l:
        return {"status_code": 301, "message": "error logging request"}
    if tokens[ip]['exp'] < datetime.now():
        print({"status_code": 309, "message": "handshake again"})
        return {"status_code": 309, "message": "handshake again"}
    tokens[ip]['exp'] = datetime.now() + timedelta(minutes=session_exp_time)
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


countryCodes = {"Egypt":"+20","USA":"+1"}  # Example list of allowed countries
lvl1Max=1000
lvl2Max=10000
lvl3Max=100000
tokenLen = 16


origins = [

    "http://localhost",
    "http://localhost:8080",
]


@router.post("/createQR")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["id", "accountNumber",'currency','amount']
        pp = preprocess(payload, names, "/createQR",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /createQR body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").first()
        if not qr is None:
            return {"status_code": 401, "message": "user has active QR request"}
        q = QR(customerID = payload["id"],dateTime= datetime.now(),accountNo=payload["accountNumber"],currency=payload["currency"],amount=payload["amount"],qrStatus="pending")

        db.add(q)
        db.commit()
         

    except:
        message = "exception occurred with creating QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "QR request generated" }

@router.post("/createQRTer")
async def createQrTer(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["terminalID", "displayName",'currency','amount','merchantName']
        pp = preprocess(payload, names, "//createQRTer",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: //createQRTer body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        
        if not qr is None:
            return {"status_code": 401, "message": "terminal has active QR request"}
        
        q = QRTer(terminalID = payload["terminalID"],dateTime= datetime.now(),currency=payload["currency"],amount=payload["amount"],displayName=payload["displayName"],merchantName=payload["merchantName"],qrStatus="pending")
        

        db.add(q)
        db.commit()
        db.refresh(q)

    except Exception as e:
        message = "exception occurred with creating QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": q}


@router.post("/cancelQrTerStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["terminalID"]
        pp = preprocess(payload, names, "/cancelQrTerStatus",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /cancelQrTerStatus body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this terminal"}

        db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").update(
            {"qrStatus": "cancelled"})
        r =requests.post("http://192.223.11.185:8080/transaction", json={ "customerID": "None","displayName":qr.displayName,"accountNo":"None","message":"transaction registered","transactionStatus":"cancelled","transactionID":"None","terminal":qr.terminalID,"amount":qr.amount,"currency":qr.currency})
        db.commit()

    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Payment has been cancelled"}

@router.post("/timeOutQrTerStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["terminalID"]
        pp = preprocess(payload, names, "/timeOutQrTerStatus",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /timeOutQrTerStatus body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this terminal"}

        db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").update(
            {"qrStatus": "timed out"})
        r =requests.post("http://192.223.11.185:8080/transaction", json={ "customerID": "None","displayName":qr.displayName,"accountNo":"None","message":"transaction registered","transactionStatus":"timed out","transactionID":"None","terminal":qr.terminalID,"amount":qr.amount,"currency":qr.currency})
        db.commit()

    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Payment Timed Out"}


@router.post("/rejectQrTerStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["terminalID"]
        pp = preprocess(payload, names, "/rejectQrTerStatus",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /rejectQrTerStatus body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this terminal"}

        db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").update(
            {"qrStatus": "rejected"})
        r =requests.post("http://192.223.11.185:8080/transaction", json={ "customerID": "None","displayName":qr.displayName,"accountNo":"None","message":"transaction registered","transactionStatus":"rejected","transactionID":"None","terminal":qr.terminalID,"amount":qr.amount,"currency":qr.currency})
        db.commit()

    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "Qr request rejected"}

@router.get("/getQrTerStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["terminalID"]
        pp = preprocess(payload, names, "/getQrTerStatus",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /getQrTerStatus body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"], QRTer.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this terminal"}
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr}#,"customer":cus }


@router.get("/getQrTerIdStatus")
async def getqrter(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["qrID"]
        pp = preprocess(payload, names, "/getQrTerIdStatus",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /getQrTerIdStatus body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        qr = db.query(QRTer).filter(QRTer.id == payload["qrID"]).first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this id"}

    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr}  # ,"customer":cus }


@router.post("/recCancelQr")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["id"]
        pp = preprocess(payload, names, "/recCancelQr",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /recCancelQr body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "user has no active QR request"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").update({"qrStatus":"cancelled"})
        db.commit()
         

    except:
        message = "exception occurred with creating QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "QR request cancelled" }

@router.post("/timeOutCancelQr")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["id"]
        pp = preprocess(payload, names, "/timeOutCancelQr",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /timeOutCancelQr body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "user has no active QR request"}
        qr = db.query(QR).filter(QR.customerID == payload["id"], QR.qrStatus == "pending").update({"qrStatus":"timed out"})
        db.commit()
         

    except:
        message = "exception occurred with creating QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": "QR request timed out" }

@router.post("/senderReadQr")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["id",'recID']
        pp = preprocess(payload, names, "/senderReadQr",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /senderReadQr body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        rec = db.query(Customer).filter(Customer.id == payload["recID"]).first()
        if rec is None:
            return {"status_code": 401, "message": "no customer exists with this receiving id"}
        
        qr = db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this user"}
        db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").update({"qrStatus":"received"})
        db.commit()
        db.refresh(qr)
         
        db.refresh(rec)
        db.refresh(cus)
        
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr,"customer":cus,"receiver":rec }

@router.post("/senderRejectQr")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["id",'recID']
        pp = preprocess(payload, names, "/senderRejectQr",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /senderRejectQr body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        rec = db.query(Customer).filter(Customer.id == payload["recID"]).first()
        if rec is None:
            return {"status_code": 401, "message": "no customer exists with this receiving id"}
        qr = db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this user"}
        db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").update({"qrStatus":"rejected"})
        db.commit()
        db.refresh(qr)
         
        db.refresh(rec)
        db.refresh(cus)
        
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr,"customer":cus,"receiver":rec }

@router.get("/getQrStatus")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["id",'recID']
        pp = preprocess(payload, names, "/getQrStatus",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /getQrStatus body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        rec = db.query(Customer).filter(Customer.id == payload["recID"]).first()
        if rec is None:
            return {"status_code": 401, "message": "no customer exists with this receiving id"}
        qr = db.query(QR).filter(QR.customerID == payload["recID"], QR.qrStatus == "pending").first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this user"}
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr,"customer":cus,"receiver":rec }

@router.get("/getQrTerStatus")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["terminalID"]
        pp = preprocess(payload, names, "/getQrTerStatus",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /getQrTerStatus body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        qr = db.query(QRTer).filter(QRTer.terminalID == payload["terminalID"]).first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this user"}
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr}


@router.get("/getQrIdStatus")
async def createPin(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["terminalID"]
        pp = preprocess(payload, names, "/getQrIdStatus",request.client.host)
        if not pp["status_code"] == 200:
            log("error", "IP: " + request.client.host + " time: " + str(datetime.now()) + " api: /getQrIdStatus body: " + str(
                pp["payload"]) + " response: " + str(pp["status_code"]) + " " + str(pp["message"]))
            return pp
        payload = pp["payload"]
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code": 401, "message": "no customer exists with this id"}
        rec = db.query(Customer).filter(Customer.id == payload["recID"]).first()
        if rec is None:
            return {"status_code": 401, "message": "no customer exists with this receiving id"}
        qr = db.query(QR).filter(QR.id == payload["qrID"]).first()
        if qr is None:
            return {"status_code": 401, "message": "no QR request active by this ID"}
        elif not (qr.customerID == payload["id"] or qr.customerID == payload["recId"]) :
            return {"status_code": 401, "message": "this QR is not issued by this user"}
        
    except:
        message = "exception occurred with getting QR request"
        log(0, message)
        return {"status_code": 401, "message": message}

    return {"status_code": 201, "message": qr,"customer":cus,"receiver":rec }