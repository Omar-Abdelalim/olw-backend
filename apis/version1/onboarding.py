from http.client import HTTPException

from fastapi import APIRouter, Depends, Header, Request, Body, Response, status,HTTPException
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

from db.globals.global_variables import tokens
from apis.version1.encyption import decrypt, encrypt, DecryptRequest, decrypt_data

import requests
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from core.hashing import Hasher

router = APIRouter()

numberOfOPTTrials = 3
countryCodes = {"Egypt": "+20", "USA": "+1","KSA":"+966"}  # Example list of allowed countries
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

def log(filename,line):
    try:
        with open('../logs/' + filename+".txt", 'a+') as file:
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
def preprocess(data: DecryptRequest,names,requ):
    
    p = data
    print("from check phone",p)

    p = p.replace("'",'\"')
    p =  json.loads(p)
    l = log("requests","time: "+str(datetime.now())+" api: "+requ+" body: "+str(p))
    if not l:
        return {"status_code": 301 , "message": "error logging request"}
    for i in names:
        if i not in p:
            return {"status_code": 400 , "message": "missing variable: "+i}        
    return {"status_code": 200, "message": "payload edited","payload":p}

def generateOTP(length):
    return "".join(random.choice('0123456789') for _ in range(length))

def generate_bank_account(customerID,account_type=1, sub_account=1, currency_code=1):
    last_account_number = int(customerID) + 100
    

    account_type_str = f"{int(account_type):02}"
    sub_account_str = f"{int(sub_account):03}"
    currency_code_str = f"{int(currency_code):02}"

    account_number_str = f"{last_account_number:08}"
    bank_account = f"{account_type_str}-{account_number_str}-{sub_account_str}-{currency_code_str}"

    return bank_account
    

class DecryptRequest(BaseModel):
    message: str


@router.post("/checkPhone")
async def checkPhone(request: Request, response: Response, data: DecryptRequest, db: Session = Depends(get_db)):
    names = ["phoneNumber","countryCode"]
    pp = preprocess(data,names,"/checkPhone")
    if not pp["status_code"] == 200:
        log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkPhone body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
        return pp
    pay = pp["payload"]
    print(pp['payload'])

    cus = db.query(Customer).filter(Customer.countryCode == pay["countryCode"],Customer.phoneNumber == pay["phoneNumber"],not Customer.status == "inactive").first()
    if cus is None :
        return {"status_code":200,"message":"this phone number is available"}
    log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkPhone body: "+str(pay)+" response: 401 this phone number is taken")
    oo = db.query(OTP).filter(OTP.countryCode == pay["countryCode"],OTP.phoneNumber== pay["phoneNumber"],OTP.status == "complete").first()
    if oo is None:
        return encrypt(str({"status_code":200,"message":"this phone number is available"}),request.client.host)

    return encrypt(str({"status_code":401,"message":"this phone number is taken"}),request.client.host)
    # except Exception as e:
    #     message = "exception "+str(e)+" occurred with checking phone"
    #     log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkPhone response: "+str(e))
    #     return {"status_code": 401, "message": message}

@router.post("/createOTP")
async def createOTP(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["phoneNumber","countryCode"]
        pp = preprocess(payload,names,"/createOTP")
        if not pp["status_code"] == 200:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createOTP body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]
        oold = db.query(OTP).filter(OTP.countryCode == pay["countryCode"],OTP.phoneNumber == pay["phoneNumber"],OTP.status == "pending").first()
        if not oold is None:
            db.query(OTP).filter(OTP.countryCode == pay["countryCode"],OTP.phoneNumber == pay["phoneNumber"],OTP.status == "pending").update({"status":"expired"})
        o = OTP(dateTime = datetime.now(),phoneNumber = pay["phoneNumber"],countryCode = pay["countryCode"],otp = generateOTP(OTPLength),status = "pending",remainingTrials = numberOfOPTTrials,timeoutTime=datetime.now()+timedelta(minutes=OTPvalidMinutes))
        db.add(o)
        db.commit()
        return {"status_code":200,"message":"OTP is generated","otp":o.otp}
    except Exception as e:
        message = "exception "+str(e)+" occurred with creating otp"
        log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createOTP response: "+str(e))
        return {"status_code": 401, "message": message}

@router.post("/checkOTP")
async def checkOTP(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["phoneNumber","countryCode","code"]
        pp = preprocess(payload,names,"/checkOTP")
        if not pp["status_code"] == 200:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkOTP body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]
        o = db.query(OTP).filter(OTP.countryCode == pay["countryCode"],OTP.phoneNumber == pay["phoneNumber"],OTP.status == "pending").first()
        if o is None:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 401 no otp waiting for this number")
            return {"status_code": 401 , "message": "no otp waiting for this number"}
        elif o.status == "expired":
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 401 otp expired please create a new one")
            return {"status_code": 401 , "message": "otp expired please create a new one"}
        elif datetime.now() > datetime.strptime(o.timeoutTime, '%Y-%m-%d %H:%M:%S.%f'):
            db.query(OTP).filter(OTP.id == o.id).update({"status":"expired"})
            db.commit()
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 401 otp expired please create a new one")
            return {"status_code": 401 , "message": "otp expired please create a new one"}
        elif not o.otp == pay["code"]:
            if o.remainingTrials == 1:
                db.query(OTP).filter(OTP.id == o.id).update({"remainingTrials":o.remainingTrials-1,"status":"expired"})
                db.commit()
                log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 402 incorrect OTP, trials expired")
                return {"status_code": 402 , "message": "incorrect OTP","trials remaining":o.remainingTrials}    
            db.query(OTP).filter(OTP.id == o.id).update({"remainingTrials":o.remainingTrials-1})
            db.commit()
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 402 incorrect OTP, "+str(o.remainingTrials)+" trials remaining")
            return {"status_code": 402 , "message": "incorrect OTP","trials remaining":o.remainingTrials}
        db.query(OTP).filter(OTP.id == o.id).update({"status":"complete"})
        db.commit()
        return {"status_code":200,"message":"OTP successfully entered"}
    except Exception as e:
        message = "exception "+str(e)+" occurred with entering otp"
        log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /checkOTP response: "+str(e))
        return {"status_code": 401, "message": message}

@router.post("/createCustomer")
async def createCustomer(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["phoneNumber","countryCode","ID/Iqama","DOB","firstName","lastName"]
        pp = preprocess(payload,names,"/createCustomer")
        if not pp["status_code"] == 200:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createCustomer body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]

        cus = db.query(Customer).filter(Customer.countryCode == pay["countryCode"],Customer.phoneNumber == pay["phoneNumber"],not Customer.status == "inactive").first()
        if not cus is None : 
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createCustomer body: "+str(pay)+" response: 401 phone number is taken")
            return {"status_code":401,"message":"this phone number is taken"}
        
        oold = db.query(OTP).filter(OTP.countryCode == pay["countryCode"],OTP.phoneNumber == pay["phoneNumber"],OTP.status == "complete").first()
        if oold is None:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createCustomer body: "+str(pay)+" response: 401 phone number not confirmed")
            return {"status_code": 401 , "message": "phone number not confirmed"}
        
        #YAKEEN and SAMA screaning 


        bDate=datetime.strptime(pay["DOB"], '%Y-%m-%d')
        bDate = bDate.replace(year=(bDate.year+18))
        if datetime.now() < bDate:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createCustomer body: "+str(pay)+" response: 402 less than 18 years")
            return {"status_code": 402 , "message": "you have to be older than 18 years to sign up"}
        
        c = Customer(dateTime = datetime.now(),phoneNumber = pay["phoneNumber"],countryCode = pay["countryCode"],nationalInterID=pay["ID/Iqama"],birthDate=pay["DOB"],status="pending",firstName=pay["firstName"],lastName=pay["lastName"])
        if "email" in  pay:
            c.email = pay["email"]    
        db.add(c)
        db.commit()
        db.refresh(c)
        return {"status_code":200,"message":"customer created","customer":c}
    except Exception as e:
        message = "exception "+str(e)+" occurred with creating account"
        log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createCustomer response: "+str(e))
        return {"status_code": 401, "message": message}

@router.post("/verifyingCustomer")
async def verifyCustomer(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["customerID"]
        pp = preprocess(payload,names,"/verifyingCustomer")
        if not pp["status_code"] == 200:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]

        cus = db.query(Customer).filter(Customer.id == pay["customerID"]).first()
        if not cus is None : 
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pay)+" response: 401 customer doesn't exist")
            return {"status_code":401,"message":"no customer has this ID"}
        elif cus.status == "inactive":
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pay)+" response: 401 customer inactive")
            return {"status_code":401,"message":"no active customer has this ID"}
        
        if cus.status == "pending":
            if not True :#FOCAL SANCTION LISTING
                log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pay)+" response: 301 customer await compliance team response (Focal Sanction)")
                return {"status_code":301,"message":"your request is being reviewed, this might take up to one working day"}
            db.query(Customer).filter(Customer.id == cus.id).update({"status":"Fapproved"})
            db.commit()
            db.refresh(cus)

        if cus.status == "Fapproved":
            if not True :#risk assessment
                log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pay)+" response: 301 customer await compliance team response (risk assessment)")
                return {"status_code":301,"message":"your request is being reviewed, this might take up to one working day"}
            db.query(Customer).filter(Customer.id == cus.id).update({"status":"Rapproved"})
            db.commit()
            db.refresh(cus)

        if cus.status == "Rapproved":
            if not True :#nafath
                log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer body: "+str(pay)+" response: 302 customer failed Nafath screening")
                return {"status_code":301,"message":"We cannot verify your identity\nWe are sorry, we cannot confirm your identity as with your National ID and your Mobile number."}
            db.query(Customer).filter(Customer.id == cus.id).update({"status":"approved"})
            db.commit()
            db.refresh(cus)

        
        return {"status_code":200,"message":"customer has been approved","customer":cus}
    except Exception as e:
        message = "exception "+str(e)+" occurred with verifying account"
        log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /verifyingCustomer response: "+str(e))
        return {"status_code": 401, "message": message}

@router.post("/createAccount")
async def createAccount(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["customerID","balance","friendlyName","iBan","accountType"]
        pp = preprocess(payload,names,"/createAccount")
        if not pp["status_code"] == 200:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createAccount body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]

        cus = db.query(Customer).filter(Customer.id == pay["customerID"]).first()
        if not cus is None : 
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createAccount body: "+str(pay)+" response: 401 customer doesn't exist")
            return {"status_code":401,"message":"no customer has this ID"}
        elif cus.status == "inactive":
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createAccount body: "+str(pay)+" response: 401 customer inactive")
            return {"status_code":401,"message":"no active customer has this ID"}
        
        if not cus.status == "approved":
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createAccount body: "+str(pay)+" response: 401 customer not fully verified")
            return {"status_code":401,"message":"customer not verfied, can't create account"}
        if not True :#risk assessment
                log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createAccount body: "+str(pay)+" response: 401 iBan not correct")
                return {"status_code":401,"message":"iBan incorrect"}    
        oldAccts = db.query(Account).filter(Account.customerID == pay["customerID"]).all()
        a = Account(customerID = pay["customerID"],dateTime= datetime.now(),accountStatus = "active",accountNumber = generate_bank_account(pay["customerID"],sub_account=len(oldAccts)+1),accountType = pay["accountType"],primaryAcount = len(oldAccts) == 0,balance=pay["balance"],country="KSA",currency="SAR",friendlyName=pay["friendlyName"],iBan=pay["iBan"])
        db.add(a)
        db.query(Customer).filter(Customer.id == pay["customerID"]).update({"status":"active"})
        db.commit()
        
        db.refresh(a)
        
        return {"status_code":200,"message":"customer has been approved","customer":cus,"account":a}
    except Exception as e:
        message = "exception "+str(e)+" occurred with creating account"
        log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /createAccount response: "+str(e))
        return {"status_code": 401, "message": message}

@router.post("/addKYC")
async def addKYC(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["customerID","income","profession","employment"]
        pp = preprocess(payload,names,"/addKYC")
        if not pp["status_code"] == 200:
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /addKYC body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]

        cus = db.query(Customer).filter(Customer.id == pay["customerID"]).first()
        if not cus is None : 
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /addKYC body: "+str(pay)+" response: 401 customer doesn't exist")
            return {"status_code":401,"message":"no customer has this ID"}
        elif cus.status == "inactive":
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /addKYC body: "+str(pay)+" response: 401 customer inactive")
            return {"status_code":401,"message":"no active customer has this ID"}
        
        if not cus.status == "active":
            log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /addKYC body: "+str(pay)+" response: 401 customer not active yet")
            return {"status_code":301,"message":"customer not active, can't add KYC"}
        
        db.query(KYC).filter(KYC.customerID == pay["customerID"]).update({"status":"inactive"})
        k = KYC(customerID = pay["customerID"],dateTime= datetime.now(),status = "active",income = pay["income"],profession = pay["profession"],employment = pay["employment"])
        db.add(k)
        db.commit()
        
        db.refresh(k)
        
        return {"status_code":200,"message":"customer kyc has been added","customer":cus,"kyc":k}
    except Exception as e:
        message = "exception "+str(e)+" occurred with creating kyc"
        log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /addKYC response: "+str(e))
        return {"status_code": 401, "message": message}
