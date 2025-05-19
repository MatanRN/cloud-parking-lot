# Cloud Parking Lot System

A serverless parking lot management system built with AWS CDK, providing automated entry and exit handling with dynamic pricing.

## Features

- Serverless architecture using AWS Lambda and API Gateway
- DynamoDB for ticket storage and management
- Automated entry and exit processing
- Dynamic pricing based on parking duration
- RESTful API endpoints for parking operations

## API Endpoints

### Entry
- **POST** `/entry`
- Query Parameters:
  - `plate`: Vehicle license plate
  - `parkingLotId`: Parking lot identifier

### Exit
- **POST** `/exit`
- Query Parameters:
  - `ticketId`: Parking ticket identifier

## Pricing

- $10 per hour
- Billed in 15-minute increments
- Minimum charge: $2.50 (15 minutes)

## Infrastructure

Built using AWS CDK with the following components:
- DynamoDB table for ticket storage
- Lambda functions for entry and exit processing
- HTTP API Gateway for REST endpoints

## Requirements

- Python 3.9+
- AWS CDK
- AWS CLI configured with appropriate credentials

## Deployment

```bash
cd cdk
cdk deploy
``` 