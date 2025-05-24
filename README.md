# graph-tagger-agent

* Use https://graph.microsoft.com/v1.0/groups to get the distribution list id

Required Graph Permissions
* Directory.Read.All
* User.Read.All
* Mail.ReadWrite

## Overview of `agent/server.py`

The `agent/server.py` file implements a FastAPI web server that acts as a webhook endpoint for Microsoft Graph notifications. It performs the following functions:

- Receives and logs incoming HTTP requests, including Microsoft Graph change notifications.
- Handles validation tokens for webhook subscription validation.
- Authenticates to Microsoft Graph using Azure AD credentials.
- Retrieves group members from a specified distribution list.
- For each notification, fetches the relevant message and tags it with a category (e.g., "tagged").
- Iterates through group members and finds related messages in their inboxes by conversation ID, tagging them as well.
- Provides detailed logging for debugging and traceability.
