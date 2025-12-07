import uuid
import logging
from fastapi import FastAPI
from fastapi.requests import Request
import time

logger = logging.getLogger("uvicorn.errors")

def register_middleware(app: FastAPI):

    @app.middleware('http')
    async def request_meta(request: Request, call_next):
        # assign an id to the request
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # process the request and measure its time
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time

        logger.info(f'Request {request_id} completed in {processing_time} seconds.')
        return response
