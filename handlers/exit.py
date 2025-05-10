"""
Exit Lambda Function

This function handles parking lot exit events.

Request Format:
GET /exit?ticketId=123e4567-e89b-12d3-a456-426614174000

Response Schema:
{
    "ticketId": "123e4567-e89b-12d3-a456-426614174000",
    "plate": "ABC123",
    "parkingLotId": "lot-001",
    "entryTs": 1620000000,
    "exitTs": 1620010000,
    "durationMin": 167,
    "chargeUsd": 70.0,
    "status": "CLOSED"
}

Errors:
- 400: Invalid input (missing ticketId)
- 404: Ticket not found or already closed
- 500: Server error
"""

import os
import json
import math
import time
from decimal import Decimal
from typing import Any, Dict

import boto3

# Initialize AWS resources
dynamodb = boto3.resource("dynamodb")
ticket_table = dynamodb.Table(os.environ.get("TICKET_TABLE"))


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle parking lot exit event.

    Updates the ticket in DynamoDB with exit information and calculates the fee.
    """
    try:
        # Parse query parameters
        query_parameters = event.get("queryStringParameters", {})
        if query_parameters is None:
            query_parameters = {}

        # Validate required fields
        if "ticketId" not in query_parameters:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: ticketId"}),
            }

        ticket_id = query_parameters["ticketId"]

        # Get ticket from DynamoDB
        response = ticket_table.get_item(Key={"ticketId": ticket_id})

        # Check if ticket exists
        if "Item" not in response:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Ticket not found"}),
            }

        ticket = response["Item"]

        # Check if ticket is already closed
        if ticket["status"] != "OPEN":
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Ticket is already closed"}),
            }

        # Calculate exit information
        exit_timestamp = int(time.time())
        entry_timestamp = ticket["entryTs"]

        # Calculate duration in minutes and round up
        diff_seconds = exit_timestamp - entry_timestamp
        diff_minutes = math.ceil(diff_seconds / 60)

        # Calculate charge: $10/hr in 15-minute chunks
        chunks = math.ceil(diff_minutes / 15)
        charge_usd = (10 / 4) * chunks

        # Update ticket in DynamoDB
        updated_ticket = ticket_table.update_item(
            Key={"ticketId": ticket_id},
            # status is a reserved word in DynamoDB, so we use an expression attribute name - #s
            UpdateExpression="SET exitTs = :exit_ts, durationMin = :duration, chargeUsd = :charge, #s = :status",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":exit_ts": exit_timestamp,
                ":duration": diff_minutes,
                ":charge": Decimal(str(charge_usd)),
                ":status": "CLOSED",
            },
            ReturnValues="ALL_NEW",
        )

        result = updated_ticket["Attributes"]

        # Return success response
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result),
        }

    except Exception as e:
        print(f"Error processing exit request: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"error": "Internal server error", "exception": f"{str(e)}"}
            ),
        }
