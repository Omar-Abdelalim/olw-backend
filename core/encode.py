from cryptography.fernet import Fernet

def encode(body,key):
    key = "a"
    key = Fernet.generate_key()
    key = "0000000000000000000000000000000000000000000="
    
    cipher_suite = Fernet(key)
    tt = cipher_suite.encrypt("0".encode()).decode()
    return {key,tt}

def decode(body):
    key = "0000000000000000000000000000000000000000000="
    
    cipher_suite = Fernet(key)
    decoded_text = cipher_suite.decrypt(body.encode()).decode()
    return body
