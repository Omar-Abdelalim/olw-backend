from fastapi import APIRouter, Depends, Header, Request, Body, Response, status
from sqlalchemy.orm import Session
from db.session import get_db
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import os
from fastapi import FastAPI
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import rsa

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

@router.post("/handshake/")
def decrypt_message(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    ciphertext = base64.b64decode(payload['message'])
    plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA1()),
        algorithm=hashes.SHA256(),
        label=None
    )
    )

    plaintext2_str = plaintext.decode('utf-8')
    return {"decrypted_message": plaintext2_str}
