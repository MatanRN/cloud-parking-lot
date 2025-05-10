"""
Parking Lot CDK App

This is the entry point for the AWS CDK application.
"""

import aws_cdk as cdk
from parking_lot_stack import ParkingLotStack


app = cdk.App()
ParkingLotStack(app, "ParkingLotStack")

app.synth()
