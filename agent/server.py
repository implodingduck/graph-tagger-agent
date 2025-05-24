from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import logging
from logging.config import dictConfig
from .log_config import log_config
import json
import os

from azure.identity.aio import ClientSecretCredential

from msgraph import GraphServiceClient
from msgraph.generated.models.message import Message

from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import MessagesRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration

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
    logger.info(f"Received notification body: {body}")
    logger.info(f"Received notification query_params: {dict(request.query_params)}")
    if "validationToken" in dict(request.query_params):
        logger.info(f"Received validation token: {request.query_params['validationToken']}")
        return PlainTextResponse(request.query_params["validationToken"])
    
    # Process the notification (this is just a placeholder)
    # You can add your processing logic here

    body_json = json.loads(body)
    credentials = ClientSecretCredential(
        os.environ.get('GRAPH_TENANT_ID'),
        os.environ.get('GRAPH_CLIENT_ID'),
        os.environ.get('GRAPH_CLIENT_SECRET'),
    )
    scopes = ['https://graph.microsoft.com/.default']
    client = GraphServiceClient(credentials=credentials, scopes=scopes)
    members = await client.groups.by_group_id(os.environ.get("GRAPH_DL_ID")).members.get()
    for member in members.value:
        print(member.display_name)


    for notification in body_json['value']:
        # Process each notification
        logger.info(f"Processing notification: {notification}")
        # Example: Get the resource URL from the notification
        resource_url = notification['resource']
        logger.info(f"Resource URL: {resource_url}")
        resource_parts = resource_url.split('/')
        user_id = resource_parts[1]
        message_id = resource_parts[3]

        # Get the message ID from the notification
        message = await client.users.by_user_id(user_id).messages.by_message_id(message_id).get()
        body_content = message.body.content
        logger.info(f"Message: {body_content}")
        logger.info(f"Message subject: {message.subject}")
        logger.info(f"Message conversation_id: {message.conversation_id}")
        logger.info(f"Message conversation_index: {message.conversation_index}")

        # Add the tagged category to the message
        update_message = Message(
            categories=["tagged"]
        )
        await client.users.by_user_id(user_id).messages.by_message_id(message_id).patch(update_message)

        # Get the members of the distribution list
        for member in members.value:
            logger.info(f"Processing member: {member.display_name}")
            # filter user messages by conversation_id
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                filter=f"conversationId eq '{message.conversation_id}'",
            )

            request_configuration = RequestConfiguration(
                query_parameters = query_params,
            )

            member_messages = await client.users.by_user_id(member.id).mail_folders.by_mail_folder_id('inbox').messages.get(request_configuration = request_configuration)
            # check if member_messages is not empty
            if not member_messages.value:
                logger.info(f"No messages found for member: {member.display_name}")
                continue
            else:
                logger.info(f"Found {len(member_messages.value)} messages for member: {member.display_name}")
                for member_message in member_messages.value:
                    logger.info(f"Member message id: {member_message.id}")
                    # tag the member message with the same category
                    await client.users.by_user_id(member.id).messages.by_message_id(member_message.id).patch(update_message)
        

    return {"status": "success", "message": "Notification received"}
