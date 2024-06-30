from fastapi import APIRouter, Depends, Header, Request, Body, Response, status, HTTPException, FastAPI, Request

from starlette.middleware.base import BaseHTTPMiddleware
import time
from apis.version1.encyption import decrypt, encrypt, decrypt_data
import json
from starlette.responses import JSONResponse

from pydantic import BaseModel


class DecryptRequest(BaseModel):
    message: str


class decryptMiddleware(BaseHTTPMiddleware):
    def decrypt_message_again(self, data: DecryptRequest):
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

        return {"message": plaintext2_str}

    async def dispatch(self, request: Request, call_next):



      body = await request.body()
      json_body = json.loads(body)
      decrypt_request = DecryptRequest(**json_body)
      decrypted_message = self.decrypt_message_again(decrypt_request)
      modified_body =  json.dumps(decrypted_message).encode('utf-8') # Modify if necessary

      # Define a new receive function that returns the modified body
      async def receive() -> dict:
          return {"type": "http.request", "body": modified_body}

      new_request = Request(scope=request.scope, receive=receive)

      response = await call_next(new_request)

      # out_resp = encrypt(response,request.client.host)
      response_body = [section async for section in response.__dict__['body_iterator']]
      response_body_str = b"".join(response_body).decode('utf-8')
      print("response i m waitting",response_body_str)

      out_resp = encrypt(response_body_str,request.client.host)

      return JSONResponse(content=out_resp)



