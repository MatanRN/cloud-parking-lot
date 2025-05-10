"""
Entry Lambda Function

This function handles parking lot entry events.

Request Format:
GET /entry?plate=ABC123&parkingLotId=lot-001

Response Schema:
{
    "ticketId": "123e4567-e89b-12d3-a456-426614174000",
    "plate": "ABC123",
    "parkingLotId": "lot-001",
    "entryTs": 1620000000,
    "status": "OPEN"
}

Errors:
- 400: Invalid input (missing required fields)
- 500: Server error
"""

import json
import os
import time
import uuid
from typing import Any, Dict

import boto3

# Initialize AWS resources
dynamodb = boto3.resource("dynamodb")
ticket_table = dynamodb.Table(os.environ.get("TICKET_TABLE"))


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle parking lot entry event.

    Creates a new ticket entry in DynamoDB and returns the ticket details.
    """
    try:
        # Parse query parameters
        query_parameters = event.get("queryStringParameters", {})
        if query_parameters is None:
            query_parameters = {}

        # Validate required fields
        if "plate" not in query_parameters or "parkingLotId" not in query_parameters:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "error": "Missing required fields: plate and parkingLotId are required",
                        "info": query_parameters,
                    }
                ),
            }

        # Extract fields
        plate = query_parameters["plate"]
        parking_lot_id = query_parameters["parkingLotId"]

        # Generate ticket data
        ticket_id = str(uuid.uuid4())
        entry_timestamp = int(time.time())

        # Create ticket item
        ticket = {
            "ticketId": ticket_id,
            "plate": plate,
            "parkingLotId": parking_lot_id,
            "entryTs": entry_timestamp,
            "status": "OPEN",
        }

        # Save to DynamoDB
        ticket_table.put_item(Item=ticket)

        # Return success response
        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(ticket),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"error": "Internal server error", "exception": f"{str(e)}"}
            ),
        }
