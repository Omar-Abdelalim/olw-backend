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


from db.globals.global_variables import tokens

import requests
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from core.hashing import Hasher
from core.encode import encode,decode

router = APIRouter()

numberOfOPTTrials = 3
countryCodes = {"Egypt": "+20", "USA": "+1","KSA":"+966"}  # Example list of allowed countries
OTPvalidMinutes = 10
OTPLength = 4

origins = [

    "http://localhost",
    "http://localhost:8080",
]


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

    


@router.post("/test")
async def test(request: Request, response: Response, data: dict = Body(...), db: Session = Depends(get_db)):
    print(json.loads(data['message']))
    return json.loads(data['message'])
    try:
        if not "none" in tokens:
            return "empty"

        # a= encode(payload["str"],"key")
        # b = decode()
        # #return request.url
    except Exception as e:
        message = "exception "+str(e)+" occurred"
        log("error","IP: "+request.client.host+" time: "+str(datetime.now())+" api: /addKYC response: "+str(e))
        return {"status_code": 401, "message": message}

@router.post("/testDisp")
async def test(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
        return tokens
    
@router.post("/test2")
async def test(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    tokens["none"] = "true"