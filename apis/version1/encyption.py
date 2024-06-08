from fastapi import APIRouter, Depends, Header, Request, Body, Response, status
from sqlalchemy.orm import Session
from db.session import get_db
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import padding as pa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
from fastapi import FastAPI
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import os
from fastapi import FastAPI
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

from db.globals.global_variables import tokens
session_exp_time = 10 #minutes


router = APIRouter()

numberOfOPTTrials = 3
countryCodes = {"Egypt": "+20", "USA": "+1","KSA":"+966"}  # Example list of allowed countries
OTPvalidMinutes = 10
OTPLength = 4

origins = [

    "http://localhost",
    "http://localhost:8080",
]

with open('keys/private_key.pem', 'rb') as private_file:
    private_pem = private_file.read()
private_key = serialization.load_pem_private_key(
        private_pem,
        password=None,  # Use this if your private key is not encrypted
        backend=default_backend()
    )

def decrypt(body):
    ciphertext_b64 = body
    ciphertext = base64.b64decode(ciphertext_b64)
    plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA1()),
        algorithm=hashes.SHA256(),
        label=None
    )
    )
    
    plaintext2_str = plaintext.decode('utf-8')
    return plaintext2_str

def encrypt(body,ip):
    t = tokens[ip]
    GLOBAL_KEY = base64.b64decode('KTXBLMpA6vV3w7OFTAgfgnce8AuVRNmSsaTy5hgpHtk=')
    GLOBAL_IV = os.urandom(12)
    encrypter = Cipher(
        algorithms.AES(GLOBAL_KEY),
        modes.GCM(GLOBAL_IV),
        backend=default_backend()
    ).encryptor()

    message_bytes = body.encode()

    # Add padding to the message
    padder = pa.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(message_bytes) + padder.finalize()

    encrypted = encrypter.update(padded_data) + encrypter.finalize()
    tag = encrypter.tag

    encrypted_message_base64 = base64.b64encode(encrypted).decode("utf-8")
    iv_base64 = base64.b64encode(GLOBAL_IV).decode("utf-8")
    tag_base64 = base64.b64encode(tag).decode("utf-8")

    return {
        'encrypted_message': encrypted_message_base64,
        'iv': iv_base64,
        'tag': tag_base64
    }
    return body


@router.post("/handshake")
def decrypt_message(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    ciphertext_b64 =  payload['message']
    ciphertext = base64.b64decode(ciphertext_b64)
    plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA1()),
        algorithm=hashes.SHA256(),
        label=None
    )
    )
    
    plaintext2_str = plaintext.decode('utf-8')
    ip = request.client.host
    
    tokens [ip] = {'key':plaintext2_str,'exp':datetime.now()+timedelta(minutes=session_exp_time)}
    return {"decrypted_message": plaintext2_str,'t':tokens}