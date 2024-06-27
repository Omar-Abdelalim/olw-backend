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
# aMY IMPORT
import logging
from pydantic import BaseModel
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # Import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
from datetime import datetime

session_exp_time = 10  # minutes

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
numberOfOPTTrials = 3
countryCodes = {"Egypt": "+20", "USA": "+1", "KSA": "+966"}  # Example list of allowed countries
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


def encrypt(body, ip):
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


with open('keys/public_key.pem', 'rb') as public_file:
    public_pem = public_file.read()
public_key = serialization.load_pem_public_key(
    public_pem,
    backend=default_backend()
)


class DecryptRequest(BaseModel):
    message: str


class DecryptSessionKeyRequest(BaseModel):
    encrypted_session_key: str
    aes_key: str
    iv: str


def load_private_key():
    with open("keys/private_key.pem", "rb") as private_key_file:
        private_key = serialization.load_pem_private_key(
            private_key_file.read(),
            password=None
        )
    return private_key


def load_public_key():
    with open("keys/public_key.pem", "rb") as public_key_file:
        public_key = serialization.load_pem_public_key(
            public_key_file.read()
        )
    return public_key


@router.post("/encrypt")
def encrypt_message(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    plaintext = payload['text']

    # Encrypt the plaintext using OAEP padding
    ciphertext = public_key.encrypt(
        plaintext.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # Encode the ciphertext to base64 for easy display and storage
    ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
    print(ciphertext_b64)
    return {"decrypted_message": ciphertext_b64}


def decrypt_data(encrypted_data: str) -> bytes:
    private_key = load_private_key()
    encrypted_data_bytes = base64.b64decode(encrypted_data.encode())
    decrypted_data = private_key.decrypt(
        encrypted_data_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data


@router.post("/handshake")
def decrypt_message(request: Request, response: Response, data: DecryptRequest, db: Session = Depends(get_db)):
    # return data.message
    # return {"status":"i m working"}
    # try:
    #     logger.info("Received data for decryption.")
    #     if not data.message:
    #         logger.warning("encrypted_data field is missing in the request.")
    #         raise HTTPException(status_code=400, detail="encrypted_data field is required")
    #     decrypted_message = decrypt_data(data.message).decode()
    #     logger.info("Decryption successful.")
    #
    # except HTTPException as e:
    #     logger.error(f"HTTP error: {e.detail}")
    #     return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    # except Exception as e:
    #     logger.error(f"Unexpected error: {str(e)}")
    #     return JSONResponse(status_code=500, content={"detail": f"Unexpected error: {str(e)}"})
    # plaintext2_str = decrypted_message
    ip = request.client.host

    tokens[ip] = {'key': data.message, 'exp': datetime.now() + timedelta(minutes=session_exp_time)}
    return {"decrypted_message":  data.message, 't': tokens}