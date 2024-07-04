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


def preprocess(data: DecryptRequest, requ,ip):
    p = json.loads(data.message)

    print("from "," :", p)

    # p = p.replace("'", '\"')
    # p = json.loads(p)
    # l = log("requests", "time: " + str(datetime.now()) + " api: " + requ + " body: " + str(p))
    # if not l:
    #     return {"status_code": 301, "message": "error logging request"}
    if tokens[ip]['exp'] < datetime.now():
        print({"status_code": 309, "message": "handshake again"})
        return {"status_code": 309, "message": "handshake again"}
    tokens[ip]['exp'] = datetime.now() + timedelta(minutes=session_exp_time)
    # for i in names:
    #     if i not in p:
    #         return {"status_code": 400, "message": "missing variable: " + i}
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


@router.post("/initAccts")
async def intiAccts(request: Request=None,response: Response=None,db: Session = Depends(get_db)):
        adm = db.query(Customer).filter(Customer.status == "admin").first()
        addFee("00010001","0001","send money to wallet user",0.5,1,0,0,db)
        addFee("00010002","0001","National money transfer",0.5,1,5,1,db)
        addFee("00010003","0001","international money transfer",1,1,10,5,db)

        cur = Currency(country="USA",currencyName="USD",code="01",status="Active")
        db.add(cur)
        if not adm is None:
            db.commit()
            return {"status_code": 201,"message":"wallet initiated"}
        admin = Customer(firstName="OLW",lastName="",email="",birthDate="",status="admin",dateTime = datetime.now())
        db.add(admin)
        
        OLWBank = db.query(Account).filter(Account.accountNumber == "1").first()
        if OLWBank is None:
            olw = Account(customerID="1",accountNumber="10-00000003-001-000",accountType="OLW",balance=10000,dateTime=datetime.now(),accountStatus="Admin",primaryAccount=1,currency="UNI",country="UNI",friendlyName="bank",iBan="0")
            db.add(olw)

        OLWAudit = db.query(Account).filter(Account.accountNumber == "2").first()
        if OLWBank is None:
            olw = Account(customerID="1",accountNumber="10-00000001-001-000",accountType="OLW",balance=0,dateTime=datetime.now(),accountStatus="Admin",primaryAccount=1,currency="UNI",country="UNI",friendlyName="audit",iBan="0")
            db.add(olw)
            
        OLWFees = db.query(Account).filter(Account.accountNumber == "3").first()
        if OLWFees is None:
            olw = Account(customerID="1",accountNumber="10-00000005-001-000",accountType="OLW",balance=10000,dateTime=datetime.now(),accountStatus="Admin",primaryAccount=1,currency="UNI",country="UNI",friendlyName="fees",iBan="0")
            db.add(olw)
        with open("last_account_number.txt", "w") as file:
            file.write(str(100)) 
        
        db.commit()
        return {"status_code": 201, "message": "wallet and fees added"}


@router.post("/transaction")
async def tansaction1(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
            
             
            
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-000").first()
            OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-000").first()
            
            emailPhone = payload["phoneORemail"]
            cusPhone = db.query(Customer).filter(Customer.mobileNumber == emailPhone).first()
            
            
            if cusPhone is None:
                return{"status_code":404,"message":"Email/mobile number does not exist. Please provide a valid email or mobile number"}
            
            customerID = cusPhone.id
            
            cus = db.query(Customer).filter(Customer.id==customerID).first()
            sendCus = db.query(Customer).filter(Customer.id==payload["id"]).first()
            acc = db.query(Account).filter(Account.customerID ==customerID , Account.primaryAccount).first()
            
            if not sendCus.pin == payload["pin"]:
                return {"status_code": 401,"message":"pins don't match"}
            sendAcc = db.query(Account).filter(Account.accountNumber==payload["fromAccount"]).first()
            if payload["amount"]+payload["fees"] > sendAcc.balance:
                return {"status_code": 401,"message":"balance not enough"}
            
            if OLWBank is None or OLWBank is None:
                return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
            trans = transactionOperation(payload["fromAccount"],acc.accountNumber,payload["amount"],payload["fromCurrency"],payload["toCurrency"],db)
            if not trans["status_code"]==201:
                return trans
                        
            if payload["fees"]>0:
                trans2 = transactionOperation(payload["fromAccount"],"10-00000005-001-000",payload["fees"],payload["fromCurrency"],payload["toCurrency"],db)
                
                if not trans2["status_code"]==201:
                    return trans2
            
        except:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":message}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(payload["fromAccount"],acc.accountNumber,payload["amount"],payload["fromCurrency"],payload["toCurrency"]))
        db.commit()
         
        db.refresh(cus)
        tra1 = db.query(Transaction).filter(Transaction.id == trans["t1"]).first()
        return {"status_code": 201, "customer": cus ,"message":"transaction registered","transactions":tra1}

@router.post("/transactionQr")
async def tansaction1(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
            
             
            
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-000").first()
            OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-000").first()
            
            
            cus = db.query(Customer).filter(Customer.id==payload["recID"]).first()
            if cus is None:
                return {"status_code": 401,"message":"receiving customer doesn't exist"}
            
            sendCus = db.query(Customer).filter(Customer.id==payload["id"]).first()
            
            acc = db.query(Account).filter(Account.customerID ==payload["recID"]  ,Account.primaryAccount).first()
            if not sendCus.pin == payload["pin"]:
                return {"status_code": 401,"message":"pins don't match"}
            sendAcc = db.query(Account).filter(Account.accountNumber==payload["fromAccount"]).first()
            if payload["amount"]+payload["fees"] > sendAcc.balance:
                return {"status_code": 401,"message":"balance not enough"}
            
            if OLWBank is None or OLWBank is None:
                return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
            trans = transactionOperation(payload["fromAccount"],acc.accountNumber,payload["amount"],payload["fromCurrency"],payload["toCurrency"],db)
            if not trans["status_code"]==201:
                return trans
            q = db.query(QR).filter(QR.id == payload["qrID"]).first()
            
            if q is None:
                return{"status_code":404,"message":"no qr code exists with this ID"}
            elif q.qrStatus == "completed":
                return{"status_code":404,"message":"transaction already complete"}
            
            
            
            db.query(QR).filter(QR.id == payload["qrID"]).update({"transactionID":trans["t1"]})

            db.query(QR).filter(QR.id == payload["qrID"]).update({"qrStatus":"completed"})
            if payload["fees"]>0:
                trans2 = transactionOperation(payload["fromAccount"],"10-00000005-001-000",payload["fees"],payload["fromCurrency"],payload["toCurrency"],db)
                
                if not trans2["status_code"]==201:
                    return trans2
        except:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":message}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(payload["fromAccount"],acc.accountNumber,payload["amount"],payload["fromCurrency"],payload["toCurrency"]))
        db.commit()
         
        db.refresh(cus)
        return {"status_code": 201, "customer": cus ,"message":"transaction registered","transactions":trans["t1"]}

@router.post("/transactionMerchant")
async def tansaction1(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
        qrt = db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "pending").first()
        if qrt is None:
            return{"status_code":403,"message":"terminal qr code is not pending here"}
        db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "pending").update({"qrStatus":"processing"})
        db.commit()
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
             
            
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-000").first()


            sendCus = db.query(Customer).filter(Customer.id==payload["id"]).first()

            if not sendCus.pin == payload["pin"]:
                return {"status_code": 401,"message":"pins don't match"}

            sendAcc = db.query(Account).filter(Account.accountNumber==payload["fromAccount"]).first()
            if sendAcc is None:
                return {"status_code": 401,"message":"return account doesn't exist"}
            if payload["amount"] > sendAcc.balance:
                return {"status_code": 401,"message":"balance not enough"}

            if OLWBank is None:
                return{"status_code":404,"message":"please make sure olw bank account are intialized"}
            qrt = db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "processing").first()
            if qrt is None:
                return{"status_code":403,"message":"terminal qr code is not pending here"}
            trans = transactionOperation(payload["fromAccount"],qrt.terminalID,payload["amount"],payload["fromCurrency"],payload["toCurrency"],db,displayName="merchant:"+qrt.merchantName)

            if not trans["status_code"]==201:
                return trans

            # q = db.query(QR).filter(QR.id == payload["qrID"]).first()
            
            # if q is None:
            #     return{"status_code":404,"message":"no qr code exists with this ID"}
            # elif q.qrStatus == "completed":
            #     return{"status_code":404,"message":"transaction already complete"}


            
            db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "processing").update({"transactionID":trans["t1"]})

            db.query(QRTer).filter(QRTer.terminalID == payload["terminal"],QRTer.qrStatus == "processing").update({"qrStatus":"completed"})


        except Exception as e:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":e}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(payload["fromAccount"],payload["terminal"],payload["amount"],payload["fromCurrency"],payload["toCurrency"]))
        db.commit()
        db.refresh(sendAcc)
        db.refresh(sendCus)
        
        tra = db.query(Transaction).filter(Transaction.id == trans["t1"]).first()
        
        r =requests.post("http://192.223.11.185:8080/transaction", json={ "customerID": sendCus.id,"accountNo":sendAcc.accountNumber,"message":"transaction registered","transactionStatus":tra.transactionStatus,"transactionID":tra.id,"terminal":payload["terminal"],"amount":payload["amount"],"currency":payload["toCurrency"]})
        
        
        return {"status_code": 201, "customer": sendCus,"account":sendAcc,"message":"transaction registered","transactions":tra ,"response":r.json}


@router.post("/transactionOut")
async def tansaction2(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
             
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-000").first()
            OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-000").first()
            iBan = payload["iBan"]
            
            

            sendCus = db.query(Customer).filter(Customer.id==payload["id"]).first()
            
            
            if not sendCus.pin == payload["pin"]:
                return {"status_code": 401,"message":"pins don't match"}
            sendAcc = db.query(Account).filter(Account.accountNumber==payload["fromAccount"]).first()
            if sendAcc is None:
                return {"status_code": 401,"message":"sending account doesn't exist"}
            elif sendAcc.customerID == payload["id"]:
                return {"status_code": 401,"message":"sending account doesn't belong to this user"}
            
            if payload["amount"]+payload["fees"] > sendAcc.balance:
                return {"status_code": 401,"message":"balance not enough"}
            if OLWBank is None or OLWBank is None:
                return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
            
            trans = transactionOperation(payload["fromAccount"],iBan,payload["amount"],payload["fromCurrency"],payload["toCurrency"],db)
            if not trans["status_code"]==201:
                return trans
            
            if payload["fees"]>0:
                trans2 = transactionOperation(payload["fromAccount"],"10-00000005-001-000",payload["fees"],payload["fromCurrency"],payload["toCurrency"],db)
                
                if not trans2["status_code"]==201:
                    return trans2
        except:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":message}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(payload["fromAccount"],("iBan"+iBan),payload["amount"],payload["fromCurrency"],payload["toCurrency"]))
        db.commit()
         
        return {"status_code": 201 ,"message":"transaction registered"}        

def tansaction3(intransID,db: Session = Depends(get_db)):
        try:
            intrans = db.query(TransactionRequestIncoming).filter(TransactionRequestIncoming.id == intransID).first()
            
            if intrans == None:
                return {"status_code":404,"message":"no such transaction requested"}
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-000").first()
            OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-000").first()
            db.query(TransactionRequestIncoming).filter(TransactionRequestIncoming.id == intransID).update({"transactionStatus":"processed"})
            db.commit()
            
            if OLWBank is None or OLWBank is None:
                return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
            feesCode=intrans.feesCode
            amount=intrans.amount
            trans = transactionOperation(intrans.inIBan,intrans.accountNo,intrans.amount,intrans.sendingCurrency,intrans.currency,db)
            
            if not trans["status_code"]==201:
                return trans
            
            feeM = calcFee(db,feesCode,amount)   
            
            if not feeM["status_code"]==201:
                return feeM
            if feeM["fee"]>0:
                trans2 = transactionOperation(intrans.accountNo,"10-00000005-001-000",feeM["fee"],intrans.sendingCurrency,intrans.currency,db)
                
                if not trans2["status_code"]==201:
                    return trans2
        except:
            message = "exception occurred with creating transaction"
            log(0,message)
            return {"status_code":401,"message":message}
        log(1,"from:{}, to:{}, amount:{},sending currency:{}, receiving currency:{}".format(intrans.inIBan,intrans.accountNo,intrans.amount,intrans.sendingCurrency,intrans.currency))
        return {"status_code": 201,"message":"transaction registered"}

# @router.get("/testT")
# async def testT(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
#     try:
#         return addCharge(db,payload["id"],payload["currency"],payload["amount"],payload["feesService"],payload["feesCurr"],"card")
#     except:
#         message = "exception occurred with retrieving currencies"
#         log(0,message)
#         return {"status_code":401,"message":message}
  

@router.post("/bank")
async def createBank(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
             
            
            accountNo=payload["accountNo"]
            bankName=payload["bankName"]
            country=payload["country"]
            currency=payload["currency"]
            otherNames=payload["otherNames"]
            surName=payload["surName"]
            bankType=payload["bankType"]
            iBan=payload["iBan"]
            friendlyName=payload["friendlyName"]
            bic=payload["bic"]
            beneficiary=payload["beneficiary"]
            beneficiaryAddress=payload["beneficiaryAddress"]

            account = db.query(Account).filter(Account.accountNumber == accountNo).first()

            if account is None:
                return {"status_code":401,"message":"account number doesn't exist"}
            elif not account.currency == currency:
                return {"status_code":401,"message":"currency doesn't match account currency"}
                
                
            

            bank = addBank(db,accountNo,bankName,friendlyName,country,currency,otherNames,surName,bankType,iBan,bic,beneficiary,beneficiaryAddress)
            if not bank["status_code"] == 201:
                return bank
            db.commit()
            
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201 ,"message":"bank account created"}

@router.post("/getBanks")
async def createBank(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
             
            
            
            accountNo=payload["accountNo"]

            account = db.query(Account).filter(Account.accountNumber == accountNo and Account.customerID == payload["id"]).first()

            if account is None:
                return {"status_code":401,"message":"account doesn't exist or doesn't belong to the user with this id"}
            
            bank = db.query(Bank).filter(Bank.accountNumber == accountNo).all()

            if len(bank) == 0:
                return {"status_code":401,"message":"bank account not linked to this account"}
                
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201 ,"message":bank}

@router.post("/getBanksIban")
async def createBank(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
             
            
            
            iBan=payload["iBan"]
            bank = db.query(Bank).filter(Bank.iBan == iBan).first()
            accountNo=bank.accountNumber
            

            account = db.query(Account).filter(Account.accountNumber == accountNo and Account.customerID == payload["id"]).first()

            if account is None:
                return {"status_code":401,"message":"account doesn't exist or doesn't belong to the user with this id"}
            
            

            if bank is None:
                return {"status_code":401,"message":"bank account not linked to this account"}
                
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201 ,"message":bank}

@router.post("/bankB")
async def createBank(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
             
            
            accountNo=payload["accountNo"]
            bankName=payload["bankName"]
            country=payload["country"]
            currency=payload["currency"]
            otherNames=payload["otherNames"]
            surName=payload["surName"]
            bankType=payload["bankType"]
            iBan=payload["iBan"]
            friendlyName=payload["friendlyName"]
            bic=payload["bic"]
            beneficiary=payload["beneficiary"]
            beneficiaryAddress=payload["beneficiaryAddress"]

            account = db.query(Account).filter(Account.accountNumber == accountNo).first()

            if account is None:
                return {"status_code":401,"message":"account number doesn't exist"}
            elif not account.currency == currency:
                return {"status_code":401,"message":"currency doesn't match account currency"}
                
                
            

            bank = addBankB(db,accountNo,bankName,friendlyName,country,currency,otherNames,surName,bankType,iBan)
            if not bank["status_code"] == 201:
                return bank
            db.commit()
            
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201 ,"message":"bank account created"}        

@router.post("/getBanksB")
async def createBank(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
             
            
            
            accountNo=payload["accountNo"]
            friendlyName=payload["friendlyName"]

            account = db.query(Account).filter(Account.accountNumber == accountNo and Account.customerID == payload["id"]).first()

            if account is None:
                return {"status_code":401,"message":"account doesn't exist or doesn't belong to the user with this id"}
            
            bank = db.query(BankBusiness).filter(BankBusiness.accountNumber == accountNo).all()

            if len(bank) == 0:
                return {"status_code":401,"message":"bank account not linked to this account"}
                
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201 ,"message":bank}        

@router.post("/getBanksBIban")
async def createBank(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
        try:
            pp = preprocess(data,request.client.host)
            if not pp["status_code"] == 200:
                return pp
            payload = pp["payload"]
            
            bank = db.query(BankBusiness).filter(BankBusiness.iBan == payload["iBan"]).first()
            accountNo=bank.accountNumber
            

            account = db.query(Account).filter(Account.accountNumber == accountNo and Account.customerID == payload["id"]).first()

            if account is None:
                return {"status_code":401,"message":"account doesn't exist or doesn't belong to the user with this id"}
            
            

            if len(bank) == 0:
                return {"status_code":401,"message":"bank account not linked to this account"}
                
        except:
            message = "exception occurred with creating bank"
            log(0,message)
            return {"status_code":401,"message":message}
        return {"status_code": 201,"message":bank,"account":account}        

@router.post("/inTransaction")
async def testT(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    pp = preprocess(data,request.client.host)
    if not pp["status_code"] == 200:
        return pp
    payload = pp["payload"]
    t = TransactionRequestIncoming(dateTime = datetime.now(),inIBan=payload["inIBan"],accountNo=payload["accountNo"],currency=payload["currency"],country=payload["country"],sendingCurrency=payload["sendingCurrency"],sendingCountry=payload["sendingCountry"],direction="in",transactionStatus="pending",amount=payload["amount"],feesCode=payload["feesCode"])
    db.add(t)
    db.commit()

@router.post("/balanceBank")
async def testT(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    pp = preprocess(data,request.client.host)
    if not pp["status_code"] == 200:
        return pp
    payload = pp["payload"]
    t1 = db.query(Transaction).filter(Transaction.id%2 == 1).all()
    t2 = db.query(Transaction).filter(Transaction.id%2 == 0).all()

    transactions_data_1 = []
    for transaction in t1:
        transactions_data_1.append({
        'id': transaction.id,
        'dateTime': transaction.dateTime,
        'accountNo': transaction.accountNo,
        'outAccountNo': transaction.outAccountNo,
        'transactionStatus': transaction.transactionStatus,
        'description': transaction.description,
        'amount': transaction.amount,
        'sendID': transaction.sendID,
        'recID': transaction.recID
    })
        
    transactions_data_2 = []
    for transaction in t2:
        transactions_data_2.append({
        'id': transaction.id,
        'dateTime': transaction.dateTime,
        'accountNo': transaction.accountNo,
        'outAccountNo': transaction.outAccountNo,
        'transactionStatus': transaction.transactionStatus,
        'description': transaction.description,
        'amount': transaction.amount,
        'sendID': transaction.sendID,
        'recID': transaction.recID
    })
    
    
    df1 = pd.DataFrame(transactions_data_1)
    df2 = pd.DataFrame(transactions_data_2)

    df1['outAccountNo'] = df2['outAccountNo']
    df1['recID'] = df2['sendID']
    df1['description']=df2['description']
    df1.rename(columns={'accountNo': 'account paying','outAccountNo':'account receiving'}, inplace=True)
    df1["account receiving"][df1["account receiving"]=="10-00000005-001-000"]="Fees"
    df1["account receiving"][df1["account receiving"]=="10-00000003-001-000"]="OLW Bank"
    
    
    # df1['id'] = df1['id']/2+1
    print(df1)

    csv_file = 'transactions.csv'
    
    df1.to_csv(csv_file, index=False)
    
    

    return {"status_code": 201,"message":f"Data has been written to {csv_file}"}

def transactionOperation(sender,receiver,sendAmount,sendCurr,recCurr,db,displayName="None"):
    try:
        OLWAudit = db.query(Account).filter(Account.accountNumber == "10-00000001-001-000").first()
        
        now = datetime.now()
        recAmount = sendAmount * 1

        if OLWAudit is None:
            return {"status_code":401,"message":"Audit account not intialized"}
        
        accountSending = db.query(Account).filter(Account.accountNumber == sender).first()
        accountRec = db.query(Account).filter(Account.accountNumber == receiver).first()

        if accountSending is None and accountRec is None:
            return {"status_code":401,"message":"neither accounts is on OLW"}
        if accountSending is None:
            # if not checkExAccount(sender):
            #     return {"status_code":401,"message":"iBan does not exist"} 
            #

            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-000").first()
            accountSending=OLWBank
            currency= db.query(Currency).filter(Currency.currencyName==recCurr).first()
            
            t1 = Transaction(dateTime=now,accountNo=OLWBank.accountNumber,outAccountNo=OLWAudit.accountNumber,sendID=OLWBank.customerID,recID=OLWAudit.customerID,transactionStatus="pending",amount=recAmount,description=sender)
        else:
            t1 = Transaction(dateTime=now,accountNo=accountSending.accountNumber,outAccountNo=OLWAudit.accountNumber,sendID=accountSending.customerID,recID=OLWAudit.customerID,transactionStatus="pending",amount=sendAmount)   
        if sendAmount < 1:
            return {"status_code":401,"message":"sending amount can't be less than 0"}
        if sendAmount > accountSending.balance:
            return {"status_code":401,"message":"balance can't cover this transaction"}

        
        
        
        if accountRec is None:
            
            res  = checkExAccount(receiver)
            OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-000").first()
            accountRec=OLWBank
            if not res["status_code"]==200:
                
                
                currency= db.query(Currency).filter(Currency.currencyName==recCurr).first()
                
                tr = TransactionRequest(dateTime=datetime.now(),accountNo=accountSending.accountNumber,outIBan=receiver,transactionStatus="pending",amount=sendAmount,currency=recCurr,country=currency.country,direction="out")
                db.add(tr)
                

            
            
            desc=receiver
            if not displayName == "None":
                desc = displayName
            t2 = Transaction(dateTime=now,accountNo=OLWAudit.accountNumber,outAccountNo=OLWBank.accountNumber,sendID=OLWAudit.customerID,recID=OLWBank.customerID,transactionStatus="pending",amount=recAmount,description=desc)
        else:
            t2 = Transaction(dateTime=now,accountNo=OLWAudit.accountNumber,outAccountNo=accountRec.accountNumber,sendID=OLWAudit.customerID,recID=accountRec.customerID,transactionStatus="pending",amount=recAmount)


            
        db.add(t1)
        db.add(t2)
        db.commit()
        
        db.refresh(t1)
        db.refresh(t2)
            

        db.query(Account).filter(Account.accountNumber == accountSending.accountNumber).update({"balance":accountSending.balance-sendAmount})
        db.query(Account).filter(Account.accountNumber == "2").update({"balance":OLWAudit.balance+sendAmount})

        db.query(Transaction).filter(Transaction.id == t1.id).update({"transactionStatus":"audit"})
        db.query(Transaction).filter(Transaction.id == t2.id).update({"transactionStatus":"audit"})


        db.query(Account).filter(Account.accountNumber == "2").update({"balance":OLWAudit.balance-recAmount})
        db.query(Account).filter(Account.accountNumber == accountRec.accountNumber).update({"balance":accountRec.balance+recAmount})

        db.query(Transaction).filter(Transaction.id == t1.id).update({"transactionStatus":"complete"})
        db.query(Transaction).filter(Transaction.id == t2.id).update({"transactionStatus":"complete"})

        db.commit()
        db.refresh(t1)
        db.refresh(t2)
    except:
        message = "exception occurred with creating transaction operation"
        log(0,message)
        return {"status_code":401,"message":message}
            
    return {"status_code":201,"message":"transaction operation complete","t1":t1.id,"t2":t2.id}

def checkExAccount(terminalNumber):
    r =requests.get("http://192.223.11.185:8080/terminal", json={'id': terminalNumber})
    return json.loads(r.content)

def log(logFile,message):
    #error,transaction,login
    if logFile == 0:
        fileName = "logs/errors.txt"
    if logFile == 1:
        fileName = "logs/transactions.txt"
    if logFile == 2:
        fileName = "logs/login.txt"

    file_object = open(fileName,'a')
    file_object.write(message+'\n')
    file_object.close()
    return True

def addFee(feeCode,feeGroup,feeDesc,feeRate,feeAmount,feeMax,feeMin,db):
    try:
        fee = db.query(Fee).filter(Fee.feeCode == feeCode and Fee.groupCode==feeGroup and Fee.feeStatus == "active").first()
        if not fee is None:
            return False
        f = Fee(feeCode=feeCode,groupCode=feeGroup,feeDesc=feeDesc,feeRate=feeRate,feeAmount=feeAmount,feeStatus="active",feeMax=feeMax,feeMin=feeMin)
    
        db.add(f)
    except:
        message = "exception occurred with retrieving fees"
        log(0,message)
        return {"status_code":401,"message":message}
    return {"status_code":201,"message":"fee added successfully"}

def calcFee(db,feeCode,amount):
    try:
        fee = db.query(Fee).filter(Fee.feeCode==feeCode).first()
        if fee is None:
            return {"status_code":401,"message":"no fee exists with this fee code"}
    
        feeAmount = fee.feeAmount+fee.feeRate/100*float(amount)
        if feeAmount>fee.feeMax:
            feeAmount = fee.feeMax
        if feeAmount<fee.feeMin:
            feeAmount = fee.feeMin
    except:
        message = "exception occurred with retrieving fee"
        log(0,message)
        return {"status_code":401,"message":message}
    
    return {"status_code":201,"fee":feeAmount}

def addBank(db,accountNo,bankName,friendlyName,country,currency,otherNames,surName,bankType,iBan,bic,ben,benAdd):
    try:
        bank = db.query(Bank).filter(Bank.iBan == iBan).first()
        if not bank is None:
            return {"status_code":401,"message":"bank already exists"}
        acc = db.query(Account).filter(Account.accountNumber == accountNo).first()
        if acc is None:
            return {"status_code":401,"message":"account doesn't exist"}
        bank = Bank(bankName=bankName,friendlyName=friendlyName,country=country,currency=currency,otherNames=otherNames,surName=surName,bankType=bankType,iBan=iBan,accountNumber=accountNo,bic=bic,beneficiary=ben,beneficiaryAddress=benAdd,shortDescription  ="Shor Description")
        db.add(bank)
    except:
        message = "exception occurred with retrieving banks"
        log(0,message)
        return {"status_code":401,"message":message}
    return {"status_code":201,"message":"bank added successfully"}

def addBankB(db,accountNo,bankName,friendlyName,country,currency,otherNames,surName,bankType,iBan,bic,ben,benAdd):
    try:
        bank = db.query(BankBusiness).filter(BankBusiness.iBan == iBan).first()
        if not bank is None:
            return {"status_code":401,"message":"bank already exists"}
        acc = db.query(Account).filter(Account.accountNumber == accountNo).first()
        if acc is None:
            return {"status_code":401,"message":"account doesn't exist"}
        bank = BankBusiness(bankName=bankName,friendlyName=friendlyName,country=country,currency=currency,otherNames=otherNames,surName=surName,bankType=bankType,iBan=iBan,accountNo=accountNo,bic=bic,beneficiary=ben,beneficiaryAddress=benAdd)
        db.add(bank)
    except:
        message = "exception occurred with retrieving banks"
        log(0,message)
        return {"status_code":401,"message":message}
    return {"status_code":201,"message":"bank added successfully"}


def generateToken(id):
    time = datetime.now()+timedelta(minutes=15)
    year = time.year
    month = time.month
    day = time.day
    hour = time.hour
    minute = time.minute
    zeroes = ["","","",""] #month,day,hour,minute
    if minute<10:
        zeroes[3]="0"
    if hour<10:
        zeroes[2]="0"
    if day<10:
        zeroes[1]="0"
    if month<10:
        zeroes[0]="0"
    intial = zeroes[3]+str(minute)+zeroes[0]+str(month)+zeroes[2]+str(hour)+str(year)+zeroes[1]+str(day)+str(id)
    final = ""
    for i in intial:
        final=final + str(9-int(i))
    return final

def checkToken(id,token):
    revId = token[12:]
    checker = "9999999999999"
    curCheck = checker[0:len(revId)]
    if not int(id) + int(revId) == int(curCheck):
        return False
    values = ""
    for i in token:
        values = values + str(9 - int(i))
    expiration = datetime(year=int(values[6:10]), month=int(values[2:4]), day=int(values[10:12]), hour=int(values[4:6]),
                          minute=int(values[0:2]))
    if datetime.now() > expiration:
        return False
    return True



    

@router.get("/currency")
async def testT(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    try:
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
        currencies = db.query(Currency).all()
        cur = []
        for i in currencies:
            cur.append(i.currency)
        return {"status_code":201,"currencies":cur}
    except:
        message = "exception occurred with retrieving currencies"
        log(0,message)
        return {"status_code":401,"message":message}
    
@router.get("/country")
async def testT(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    try:
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
        currencies = db.query(Currency).all()
        countries = []
        for i in currencies:
            countries.append(i.country)
        return {"status_code":201,"currencies":countries}
    except:
        message = "exception occurred with retrieving countries"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/getFees")
async def getFees(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    try:
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
        returning = calcFee(db,payload["feeCode"],payload["amount"])
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        returning["level"] = cus.customerStatus
        if returning["level"]=="third level":
            returning["limit"]=lvl3Max
        elif returning["level"]=="second level":
            returning["limit"]=lvl2Max
        else:
            returning["limit"]=lvl1Max
        
        return returning 

        
    except:
        message = "exception occurred with retrieving fees"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/getEligibility")
async def getFees(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    try:
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
         
        

        returning = {}
        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code":401,"message":"No customer exists with this ID"}
        
        returning["level"] = cus.customerStatus
        if returning["level"]=="third level":
            returning["limit"]=lvl3Max
        elif returning["level"]=="second level":
            returning["limit"]=lvl2Max
        elif returning["level"]=="first level":
            return {"status_code":401,"message":"User needs to finish KYC"}
        else:
            return {"status_code":401,"message":"User needs to confirm phone"}
        
        if payload["amount"]> returning["limit"]:
            return {"status_code":401,"message":"User level needs to increase to send this amount","level":returning["level"],"limit":returning["limit"]}

        return {"status_code":201,"message":"User eligibile to send this amount","level":returning["level"],"limit":returning["limit"] }

        
    except:
        message = "exception occurred with retrieving eligibility"
        log(0,message)
        return {"status_code":401,"message":message}

# @router.post("/charge")
# async def charge(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
#     try:
#         check = checkToken(payload["id"],payload["token"])
#         if not check:
#             return {"status_code":400,"message":"token invalid"}
        
         
        

#         cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
#         if cus is None:
#             return {"status_code":401,"message":"No customer exists with this ID"}
        
#         ch = addCharge(db,payload["id"],payload["currency"],payload["amount"],payload["feeService"],payload["feeCurrency"],payload["method"])
#         if not ch["status_code"] == 201:
#             return ch
#         charge_instance = ch["message"]
#         url = "http://192.223.11.185:9000/v1/card_process"
#         # if charge.method == "crypto":
#         #     url = "http://192.223.11.185:9000/v1/crypto_process"
#         charge_dict = {
#         'id': charge_instance.id,
#         'dateTime': charge_instance.dateTime,
#         'customerID': charge_instance.customerID,
#         'accountNo': charge_instance.accountNo,
#         'currency': charge_instance.currency,
#         'amount': charge_instance.amount+charge_instance.feesService+charge_instance.feesCurrency,
#         'feesService': charge_instance.feesService,
#         'feesCurrency': charge_instance.feesCurrency,
#         'email': charge_instance.email,
#         'firstName': charge_instance.firstName,
#         'lastName': charge_instance.lastName,
#         'address': charge_instance.address,
#         'zipcode': charge_instance.zipcode,
#         'city': charge_instance.city,
#         'country': charge_instance.country,
#         'countryCode': charge_instance.countryCode,
#         'mobilenumber': charge_instance.mobilenumber,
#         'birthDate': charge_instance.birthDate,
#         'chargeStatus': charge_instance.chargeStatus,
#         'method': charge_instance.method,
#         'transactionID': charge_instance.id,
#         'webhookID': charge_instance.webhookID
#         }
#         if payload["method"]=="card":
#             card = db.query(Card).filter(Card.token == payload["cardToken"]).first()
#             if card is None:
#                 return {"status_code":401,"message":"no card with this token"}
#             charge_dict["cardInfo"]={
#                 "cardNumber":card.cardNumber,
#                 "expMonth":card.expMonth,
#                 "expYear":card.expYear,
#                 "holderName":card.holderName,
#                 "secretNumber":card.secretNumber,
#                 "firstName":charge_instance.firstName,
#                 "lastName":charge_instance.lastName,
#                 "amount":charge_instance.amount
#             }
#             charge_dict["cardNumber"]=card.cardNumber
#             charge_dict["expMonth"]=card.expMonth
#             charge_dict["expYear"]=card.expYear
#             charge_dict["holderName"]=card.holderName
#             charge_dict["secretNumber"]=card.secretNumber
            

#         req = requests.post(url, json=json.dumps(charge_dict)) 
         
#         return {"status_code":201,"url":json.loads(req.content),"charge":charge_instance }
        
#     except:
#         message = "exception occurred with charge process"
#         log(0,message)
#         return {"status_code":401,"message":message}

@router.get("/getCharge")
async def getFees(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    try:
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
         
        

        cus = db.query(Customer).filter(Customer.id == payload["id"]).first()
        if cus is None:
            return {"status_code":401,"message":"No customer exists with this ID"}
        
        ch = db.query(Charge).filter(Charge.id == payload["chargeID"]).first()
        if ch is None:
            return {"status_code":401,"message":"No charge exists with this ID"}
        elif not int(ch.customerID) == cus.id:
            return {"status_code":401,"message":"this charge does not belong to this customer"}
        time  = datetime.strptime(ch.dateTime, '%Y-%m-%d %H:%M:%S.%f')+timedelta(minutes=20)
        if datetime.now() > time:
            db.query(Charge).filter(Charge.id == payload["chargeID"]).update({"chargeStatus":"Cancelled / Timed Out"})
            db.commit()
            db.refresh(ch)
             
            return {"status_code":401,"charge":ch ,"message":"timed out"}
        return {"status_code":201,"charge":ch ,"time":20}

        
    except:
        message = "exception occurred with retrieving eligibility"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/addCard")
async def addcard(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    try:
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
        ac = addCard(db,payload["id"],payload["cardNumber"],payload["expiryMonth"],payload["expiryYear"],payload["fName"]+" "+payload["lName"],payload["secretNumber"])
        if not ac["status_code"] == 201:
            with open("formTemplates/failure.html", "r") as file:
                html_content = file.read()
                html_content = html_content.replace('%status_code', str(ac["status_code"]))
                html_content = html_content.replace('%errorMessage', str(ac["message"]))
                
                
            return Response(content=html_content, media_type="text/html")
            
        with open("formTemplates/success.html", "r") as file:
            html_content = file.read()
            html_content = html_content.replace('%status_code', "201")
        return Response(content=html_content, media_type="text/html")

        
    except:
        message = "exception occurred with adding card"
        log(0,message)
        return {"status_code":401,"message":message}

@router.post("/removeCard")
async def addcard(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    try:
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
         
        
        card = db.query(Card).filter(Card.token == payload["cardToken"],Card.cardStatus == "active").first()
        if card is None:
            return {"status_code":401,"message":"this is not an active card"}
        
        card = db.query(Card).filter(Card.token == payload["cardToken"]).update({"cardStatus":"inactive"})
        db.commit()
         
        return {"status_code":201,"message":"card removed" }
    except:
        message = "exception occurred with adding card"
        log(0,message)
        return {"status_code":401,"message":message}



@router.get("/cardForm/{cusID}")
async def addcard(cusID,request: Request,response: Response,db: Session = Depends(get_db)):
    with open("formTemplates/cardInfo.html", "r") as file:
        html_content = file.read()
        html_content = html_content.replace('%cusID', str(AlphanumericConverter.decode(str(cusID))))
    return Response(content=html_content, media_type="text/html")

@router.post("/encodeID")
async def addcard(request: Request,response: Response, payload: dict = Body(...),db: Session = Depends(get_db)):
    # try:
    re = AlphanumericConverter.encode(payload["id"])
    return {"status_code":200,"message":re}
    # except:
    #     message = "exception occurred with encoding id"
    #     log(0,message)
    #     return {"status_code":401,"message":message}


@router.get("/getCards")
async def getcard(request: Request,response: Response, data: DecryptRequest,db: Session = Depends(get_db)):
    try:
        pp = preprocess(data,request.client.host)
        if not pp["status_code"] == 200:
            return pp
        payload = pp["payload"]
         
        
        cards = db.query(Card).filter(Card.customerID == str(payload["id"]),Card.cardStatus == "active").all()
        extracted_details = []
        for card in cards:
            details = {
                'id': card.id,
                'dateTime': card.dateTime,
                'customerID': card.customerID,
                'token': card.token,
                'holderName': card.holderName,
                'last4digits': card.cardDescription  
            }
            extracted_details.append(details)

        return {"status_code":201,"message":extracted_details }

            
    except:
        message = "exception occurred with getting card"
        log(0,message)
        return {"status_code":401,"message":message}


#x = await requests.post("http://192.223.11.185:8080/transaction", json={ "customerID": sendCus.id,"accountNo":sendAcc.accountNumber,"message":"transaction registered","transactionStatus":tra.transactionStatus,"transactionID":tra.id,"terminal":payload["terminal"],"amount":payload["amount"],"currency":payload["toCurrency"]})

@router.post("/chargeTransaction")
async def testT(request: Request,response: Response,db: Session = Depends(get_db)):
    try:
        payload = await request.body()
        payload = json.loads(payload)
        print(payload)
        OLWBank = db.query(Account).filter(Account.accountNumber == "10-00000003-001-000").first()
        OLWFees = db.query(Account).filter(Account.accountNumber == "10-00000005-001-000").first()
        
        chID = payload["chargeID"]
        charge = db.query(Charge).filter(Charge.id==chID).first()
        if charge is None:
            return {"status_code": 401,"message":"no charge with this ID"}
        cus = db.query(Customer).filter(Customer.id==charge.customerID).first()
        if cus is None:
            return {"status_code": 401,"message":"no customer for this charge"}
        
        acc = db.query(Account).filter(Account.customerID ==cus.id, Account.primaryAccount).first()
        if acc is None:
            return {"status_code": 401,"message":"this customer has no primary account"}
        if payload["status"] == "Waiting for buyer funds...":
            return {"status_code": 201,"message":"awaiting change in status"}
        elif payload["status"] == "Cancelled / Timed Out":
            db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"Cancelled / Timed Out"})
            db.commit()
            return {"status_code": 201,"message":"transaction cancelled/timed out"}
        
        payload["status"] #complete,cancelled,rejected,waiting for buyer
        
        if OLWBank is None or OLWBank is None:
            return{"status_code":404,"message":"please make sure fees and bank account are intialized"}
        trans = transactionOperation(f"charge {str(charge.id)}",acc.accountNumber,charge.amount+charge.feesCurrency+charge.feesService,charge.currency,charge.currency,db)
        if not trans["status_code"]==201:
            db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"failed"})
            db.commit()
            return trans
                    
        if charge.feesCurrency>0:
            trans2 = transactionOperation(acc.accountNumber,"10-00000005-001-000",charge.feesCurrency,charge.currency,charge.currency,db)
            
            if not trans2["status_code"]==201:
                db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"failedF1"})
                db.commit()
                return trans2
        
        if charge.feesService>0:
            trans3 = transactionOperation(acc.accountNumber,"10-00000005-001-000",charge.feesService,charge.currency,charge.currency,db)
            
            if not trans3["status_code"]==201:
                db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"failedF2"})
                db.commit()
                return trans3
    except:
        message = "exception occurred with creating transaction"
        log(0,message)
        return {"status_code":401,"message":message}
    log(1,"from:OLW bank, to:{acc.accountNumber}, amount:{charge.amount},sending currency:{charge.currency}, receiving currency:{charge.currency}")
    db.query(Charge).filter(Charge.id==chID).update({"chargeStatus":"Completed","transactionID":trans["t1"],"webhookID":payload["webhookID"]})
    

    db.commit()
    db.refresh(charge)
    return {"status_code": 201,"message":"transaction completed","charge":charge}

def addCard(db,custID,cardNum,expM,expY,name,secretNum):
    try:
        cus = db.query(Customer).filter(Customer.id == custID).first()
        if cus is None:
            return {"status_code":401,"message":"customer with this ID does not exist"}
        if not len(cardNum) == 16:
            return {"status_code":401,"message":"card length needs to be 16 digits long"}
        elif int(expM)>13:
            return {"status_code":401,"message":"not valid expiry month"}
        elif int(expM)<1:
            return {"status_code":401,"message":"not valid expiry month"}
        elif int(expY)<1:
            return {"status_code":401,"message":"not valid expiry year"}
        elif not len(secretNum) == 3:
            return {"status_code":401,"message":"not valid cvv"}
        # c1 = db.query(Card).filter(Card.cardNumber == cardNum).first()
        # if c1 is None:
        #     return {"status_code":401,"message":"a card is already being used with this number"}

        ######### CAN WE ADD SAME CARD TO DIFFERENT USERS?

        alphanumeric_characters = string.ascii_letters + string.digits
        
        tok = ''.join(random.choice(alphanumeric_characters) for _ in range(tokenLen))
        c = db.query(Card).filter(Card.token == tok).first()
        while not c is None:
            tok = ''.join(random.choice(alphanumeric_characters) for _ in range(tokenLen))
            c = db.query(Card).filter(Card.token == tok).first()
        
        ca = Card(dateTime=datetime.now(),customerID=custID,token=tok,cardNumber=cardNum,expMonth=expM,expYear=expY,holderName=name,secretNumber=secretNum,cardStatus="active",cardDescription=cardNum[-4:])
        
        db.add(ca)
        db.commit()
        db.refresh(ca)
        

        return {"status_code":201,"message":ca}
    except Exception as e:
        message = "exception occurred with creating card"
        log(0,message)
        return {"status_code":401,"message":message}

# def addCharge(db,custID,curr,am,feeS,feeC,meth):
#     try:
#         cus = db.query(Customer).filter(Customer.id == custID).first()
#         if cus is None:
#             return {"status_code":401,"message":"customer with this ID does not exist"}
#         a = db.query(Account).filter(Account.customerID == cus.id,Account.primaryAccount).first()
#         if a is None:
#             return {"status_code":401,"message":"customer with this ID does not have primary account"}
#         k = db.query(KYC).filter(KYC.customerID == cus.id).first()
#         if k is None:
#             return {"status_code":401,"message":"customer with this ID does not have KYC"}
#         ad = db.query(Address).filter(Address.customerID == cus.id).first()
#         if ad is None:
#             return {"status_code":401,"message":"customer with this ID does not have address"}
#         m = db.query(Mobile).filter(Mobile.customerID == cus.id).first()
#         if m is None:
#             return {"status_code":401,"message":"customer with this ID does not have mobile"}
        
#         c = Charge(dateTime=datetime.now(),customerID=cus.id,accountNo=a.accountNumber,currency=curr,amount=am,feesService=feeS,feesCurrency=feeC,email=cus.email,firstName=cus.firstName,lastName=cus.lastName,address=ad.address1,zipcode=ad.zipCode,city=ad.city,country=ad.country,countryCode=m.countryCode,mobilenumber=m.mobileNumber,birthDate=k.birthDate,chargeStatus="pending",method=meth)
#         db.add(c)
#         db.commit()
#         db.refresh(c)

#         return {"status_code":201,"message":c}
#     except:
#         message = "exception occurred with creating charge"
#         log(0,message)
#         return {"status_code":401,"message":message}
    

class AlphanumericConverter:
    ALPHABET = 'KVEBQCUZSLFTJAIWOYNRPHXGMD'
    BASE = len(ALPHABET)
    ENCODED_LENGTH = 10

    @classmethod
    def encode(cls, number):
        binNum = format(number, '026b')
        encodedStr = ""
        for i in range(len(cls.ALPHABET)):
            if binNum[i] == "1":
                encodedStr+=cls.ALPHABET[i]
        needed = 26 -len(encodedStr)
        for i in range(needed):
            insert_position = random.randint(0, len(encodedStr))
            digit = random.randint(0,9)
            encodedStr = encodedStr[:insert_position] + str(digit) + encodedStr[insert_position:]
        return encodedStr

    @classmethod
    def decode(cls, code):
        binary_str = ""
        for char in cls.ALPHABET:
            if char in code:
                binary_str += "1"
            else:
                binary_str += "0"
        return int(binary_str, 2)