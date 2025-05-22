from fastapi import FastAPI, Request
import logging
from logging.config import dictConfig
from .log_config import log_config
import json

dictConfig(log_config)
logger = logging.getLogger("api-logger")

app = FastAPI(
    title="Graph Tagger Agent",
)

@app.middleware('http')
async def logging_middleware(request: Request, call_next):
    logger.info("logging_middleware")
    # Log method, url, headers, query params, path params, and scope
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request url: {request.url}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request query_params: {dict(request.query_params)}")
    logger.info(f"Request path_params: {request.path_params}")
    logger.info(f"Request client: {request.client}")
    logger.info(f"Request cookies: {request.cookies}")
    logger.info(f"Request scope: {json.dumps({k: str(v) for k, v in request.scope.items()})}")
    # Optionally, log the body (if needed and safe)
    body = await request.body()
    logger.info(f"Request body: {body}")
    response = await call_next(request)
    return response

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/notifications")
async def notifications(request: Request):
    # Log the request body
    body = await request.body()
    logger.info(f"Received notification: {body}")
    
    # Process the notification (this is just a placeholder)
    # You can add your processing logic here

    return {"status": "success", "message": "Notification received"}
