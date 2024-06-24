from fastapi import APIRouter, Depends, Header, Request, Body, Response, status,HTTPException,FastAPI, Request

from starlette.middleware.base import BaseHTTPMiddleware
import time
from apis.version1.encyption import decrypt, encrypt, decrypt_data
import json

from pydantic import BaseModel


class DecryptRequest(BaseModel):
    message: str


class decryptMiddleware(BaseHTTPMiddleware):
    def decrypt_message_again(self,data: DecryptRequest):

        from fastapi.responses import JSONResponse
        # try:
        if not data.message:
            raise HTTPException(status_code=400, detail="encrypted_data field is required")
        decrypted_message = decrypt_data(data.message).decode()
        # except HTTPException as e:
        #     return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        # except Exception as e:
        #     return JSONResponse(status_code=500, content={"detail": f"Unexpected error: {str(e)}"})
        plaintext2_str = decrypted_message

        print("plain text",plaintext2_str)

        return plaintext2_str
    async def dispatch(self, request: Request, call_next):
        # Code to execute before the request is processed
        start_time = time.time()
        body = await request.body()
        # Print or log the request body
        body = body.decode('utf-8')
        json_body = json.loads(body)
        print(json_body)
        decrypt_request = DecryptRequest(**json_body)
        p=self.decrypt_message_again(decrypt_request)
        print("encryptes_message",p)

        # Process the request and get the response
        response = await call_next(request)
        response.headers['encrypted_key'] = str(p)

        # Code to execute after the response is ready
        process_time = time.time() - start_time
        print(process_time)
        
        response.headers['X-Process-Time'] = str(process_time)
        
        return response


   
    
