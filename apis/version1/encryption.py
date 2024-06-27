import logging
from pydantic import BaseModel
import os
from fastapi import FastAPI, HTTPException, Request,APIRouter
from fastapi.responses import JSONResponse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # Import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
from datetime import datetime

app = APIRouter()

session_records = {}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gen_keys():
    # Generate RSA key pair (public and private keys)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # Serialize and save the private key to a file
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open("keys/private_key.pem", "wb") as private_key_file:
        private_key_file.write(private_key_pem)

    # Serialize and save the public key to a file
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("keys/public_key.pem", "wb") as public_key_file:
        public_key_file.write(public_key_pem)

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

def derive_key(password: bytes, salt: bytes, length: int = 32) -> bytes:
    # Derive a key from the password using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password)

@app.post("/encrypt/")
async def encrypt(data: dict):
    try:
        if "data" not in data:
            raise HTTPException(status_code=400, detail="data field is required")
        public_key = load_public_key()
        ciphertext = public_key.encrypt(
            data["data"].encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypted_data = base64.b64encode(ciphertext).decode()
        logger.info("Data encrypted successfully.")
        return {"encrypted_data": encrypted_data}
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class DecryptRequest(BaseModel):
    encrypted_data: str

class DecryptSessionKeyRequest(BaseModel):
    encrypted_session_key: str
    aes_key: str
    iv: str


STATIC_IV = b'\x00' * 16  # Define a static IV


@app.post("/handshake/")
async def handshake(request: Request):
    try:
        data = await request.json()
        if "encrypted_key" not in data:
            raise HTTPException(status_code=400, detail="encrypted_key field is required")

        decrypted_key = decrypt_data(data["encrypted_key"])

        # Ensure the decrypted key is 256 bits (32 bytes)
        if len(decrypted_key) < 32:
            raise HTTPException(status_code=400, detail="Decrypted key must be at least 256 bits (32 bytes) long")

        # Derive a 256-bit key from the decrypted key
        salt = os.urandom(16)
        aes_key = derive_key(decrypted_key, salt, length=32)

        # Generate a random session key
        session_key = os.urandom(32)  # 256-bit session key

        # Encrypt the session key using the derived AES key and the static IV
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(STATIC_IV))
        encryptor = cipher.encryptor()
        encrypted_session_key = encryptor.update(session_key) + encryptor.finalize()
        # Generate a session ID (e.g., a hash of the session key for simplicity)
        session_id = base64.b64encode(session_key).decode()

        # Store the record in the global dictionary
        timestamp = datetime.now().isoformat()
        session_records[session_id] = {
            "session_key": base64.b64encode(session_key).decode(),
            "random_key": base64.b64encode(decrypted_key).decode(),
            "timestamp": timestamp
        }
        print(session_records)
        return {"decrypted_session_key": base64.b64encode(encrypted_session_key).decode()}
    except HTTPException as e:
        logger.error(f"HTTP error: {e.detail}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        logger.error(f"Handshake failed: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/decrypt/")
async def decrypt(data: DecryptRequest):
    try:
        logger.info("Received data for decryption.")

        if not data.encrypted_data:
            logger.warning("encrypted_data field is missing in the request.")
            raise HTTPException(status_code=400, detail="encrypted_data field is required")

        decrypted_message = decrypt_data(data.encrypted_data).decode()
        logger.info("Decryption successful.")
        return {"decrypted_data": decrypted_message}
    except HTTPException as e:
        logger.error(f"HTTP error: {e.detail}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": f"Unexpected error: {str(e)}"})

@app.post("/decrypt-session-key/")
async def decrypt_session_key(request: Request):
    try:
        data = await request.json()
        if "encrypted_session_key" not in data or "aes_key" not in data:
            raise HTTPException(status_code=400, detail="encrypted_session_key and aes_key fields are required")

        encrypted_session_key = base64.b64decode(data["encrypted_session_key"].encode())
        aes_key = base64.b64decode(data["aes_key"].encode())

        # Decrypt the session key using the AES key
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(STATIC_IV))
        decryptor = cipher.decryptor()
        decrypted_session_key = decryptor.update(encrypted_session_key) + decryptor.finalize()

        return {"decrypted_session_key": decrypted_session_key.hex()}
    except HTTPException as e:
        logger.error(f"HTTP error: {e.detail}")
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/generate-key/")
async def generate_key():
    try:
        key = os.urandom(32)  # Generate a 256-bit key
        encoded_key = base64.b64encode(key).decode()
        logger.info("Generated 256-bit key successfully.")
        return {"key": encoded_key}
    except Exception as e:
        logger.error(f"Key generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


