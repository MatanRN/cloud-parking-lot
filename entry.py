import json
from typing import Any, Dict
import uuid
import time


def entry(event: Dict[str, Any]):
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

    # TODO: Add DB insertion
    # Return success response
    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(ticket),
    }
