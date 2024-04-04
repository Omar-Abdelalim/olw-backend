from fastapi import APIRouter, Depends, Header, Request, Body, Response, status
from sqlalchemy.orm import Session
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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db.models.account import Account
from db.models.customer import Customer
from db.models.kyc import KYC
from db.models.otp import OTP

import requests
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from core.hashing import Hasher

router = APIRouter()

numberOfOPTTrials = 3
countryCodes = {"Egypt": "+20", "USA": "+1"}  # Example list of allowed countries
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


def preprocess(payload,names,requ):
    
    p = decode(payload)
    l = log("requests","time: "+str(datetime.now())+" api: "+requ+" body: "+str(p))
    if not l:
        return {"status_code": 301 , "message": "error logging request"}
    for i in names:
        if i not in p:
            return {"status_code": 400 , "message": "missing variable: "+i}        
    return {"status_code": 200, "message": "payload edited","payload":p}

def generateOTP(length):
    return "".join(random.choice('0123456789') for _ in range(length))
    

@router.post("/checkPhone")
async def checkPhone(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["phoneNumber","countryCode"]
        pp = preprocess(payload,names,"/checkPhone")
        if not pp["status_code"] == 200:
            log("error","time: "+str(datetime.now())+" api: /checkPhone body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]
        return pay
        cus = db.query(Customer).filter(Customer.countryCode == pay["countryCode"],Customer.phoneNumber == pay["phoneNumber"],not Customer.status == "inactive").first()
        if cus is None : 
            return {"status_code":200,"message":"this phone number is available"}
        log("error","time: "+str(datetime.now())+" api: /checkPhone body: "+str(pay)+" response: 401 this phone number is taken")
        return {"status_code":401,"message":"this phone number is taken"}
    except Exception as e:
        message = "exception "+str(e)+" occurred with checking phone"
        log("error","time: "+str(datetime.now())+" api: /checkPhone response: "+str(e))
        return {"status_code": 401, "message": message}

@router.post("/createOTP")
async def createOTP(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["phoneNumber","countryCode"]
        pp = preprocess(payload,names,"/createOTP")
        if not pp["status_code"] == 200:
            log("error","time: "+str(datetime.now())+" api: /createOTP body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
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
        log("error","time: "+str(datetime.now())+" api: /createOTP response: "+str(e))
        return {"status_code": 401, "message": message}

    
@router.post("/checkOTP")
async def checkOTP(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["phoneNumber","countryCode","code"]
        pp = preprocess(payload,names,"/checkOTP")
        if not pp["status_code"] == 200:
            log("error","time: "+str(datetime.now())+" api: /checkOTP body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]
        o = db.query(OTP).filter(OTP.countryCode == pay["countryCode"],OTP.phoneNumber == pay["phoneNumber"],OTP.status == "pending").first()
        if o is None:
            log("error","time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 401 no otp waiting for this number")
            return {"status_code": 401 , "message": "no otp waiting for this number"}
        elif o.status == "expired":
            log("error","time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 401 otp expired please create a new one")
            return {"status_code": 401 , "message": "otp expired please create a new one"}
        elif datetime.now() > datetime.strptime(o.timeoutTime, '%Y-%m-%d %H:%M:%S.%f'):
            db.query(OTP).filter(OTP.id == o.id).update({"status":"expired"})
            db.commit()
            log("error","time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 401 otp expired please create a new one")
            return {"status_code": 401 , "message": "otp expired please create a new one"}
        elif not o.otp == pay["code"]:
            if o.remainingTrials == 1:
                db.query(OTP).filter(OTP.id == o.id).update({"remainingTrials":o.remainingTrials-1,"status":"expired"})
                db.commit()
                log("error","time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 402 incorrect OTP, trials expired")
                return {"status_code": 402 , "message": "incorrect OTP","trials remaining":o.remainingTrials}    
            db.query(OTP).filter(OTP.id == o.id).update({"remainingTrials":o.remainingTrials-1})
            db.commit()
            log("error","time: "+str(datetime.now())+" api: /checkOTP body: "+str(pay)+" response: 402 incorrect OTP, "+str(o.remainingTrials)+" trials remaining")
            return {"status_code": 402 , "message": "incorrect OTP","trials remaining":o.remainingTrials}
        db.query(OTP).filter(OTP.id == o.id).update({"status":"complete"})
        db.commit()
        return {"status_code":200,"message":"OTP successfully entered"}
    except Exception as e:
        message = "exception "+str(e)+" occurred with entering otp"
        log("error","time: "+str(datetime.now())+" api: /checkOTP response: "+str(e))
        return {"status_code": 401, "message": message}

@router.post("/createCustomer")
async def createOTP(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    try:
        names = ["phoneNumber","countryCode","ID/Iqama","DOB","firstName","lastName"]
        pp = preprocess(payload,names,"/createCustomer")
        if not pp["status_code"] == 200:
            log("error","time: "+str(datetime.now())+" api: /createCustomer body: "+str(pp["payload"])+" response: "+str(pp["status_code"])+" "+str(pp["message"]))
            return pp
        pay = pp["payload"]

        cus = db.query(Customer).filter(Customer.countryCode == pay["countryCode"],Customer.phoneNumber == pay["phoneNumber"],not Customer.status == "inactive").first()
        if not cus is None : 
            log("error","time: "+str(datetime.now())+" api: /createCustomer body: "+str(pay)+" response: 401 phone number is taken")
            return {"status_code":401,"message":"this phone number is taken"}
        
        oold = db.query(OTP).filter(OTP.countryCode == pay["countryCode"],OTP.phoneNumber == pay["phoneNumber"],OTP.status == "complete").first()
        if oold is None:
            log("error","time: "+str(datetime.now())+" api: /createCustomer body: "+str(pay)+" response: 401 phone number not confirmed")
            return {"status_code": 401 , "message": "phone number not confirmed"}
        
        #YAKEEN and SAMA screaning 


        bDate=datetime.strptime(pay["DOB"], '%Y-%m-%d')
        bDate = bDate.replace(year=(bDate.year+18))
        if datetime.now() < bDate:
            log("error","time: "+str(datetime.now())+" api: /createCustomer body: "+str(pay)+" response: 402 less than 18 years")
            return {"status_code": 402 , "message": "you have to be older than 18 years to sign up"}
        
        c = Customer(dateTime = datetime.now(),phoneNumber = pay["phoneNumber"],countryCode = pay["countryCode"],nationalInterID=pay["ID/Iqama"],birthDate=pay["DOB"],status="pending",firstName=pay["firstName"],lastName=pay["lastName"])
        if "email" in  pay:
            c.email = pay["email"]    
        db.add(c)
        db.commit()
        db.refresh(c)
        return {"status_code":200,"message":"customer created","customer":c}
    except Exception as e:
        message = "exception "+str(e)+" occurred with creating otp"
        log("error","time: "+str(datetime.now())+" api: /createOTP response: "+str(e))
        return {"status_code": 401, "message": message}
