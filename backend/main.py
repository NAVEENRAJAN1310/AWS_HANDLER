
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from backend.ec2_handler import (
#     start_tradingdatahandling_instance,
#     get_tradingdatahandling_ip,
#     stop_tradingdatahandling_instance,
#     instancestatus
# )
import os
import platform
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start-instance")
def start_instance():
    start_tradingdatahandling_instance()
    return {"status": "Instance start requested"}

@app.get("/getinstanceip")
def get_instance_ip():
    ip = get_tradingdatahandling_ip()
    return {"ip": ip}


@app.post("/stop-instance")
def stop_instance():
    stop_tradingdatahandling_instance()
    return {"status": "Instance stop requested"}


# New API route for instance status
@app.get("/instancestatus")
def get_instance_status():
    status = instancestatus()
    return {"status": status}

# API for password authentication
from fastapi import Request
from fastapi.responses import JSONResponse

@app.post("/password")
async def check_password(request: Request):
    data = await request.json()
    password = data.get("password")
    if password == "Madurai@123":
        return JSONResponse(content={"authentication": "success"}, status_code=200)
    else:
        return JSONResponse(content={"authentication": "failed"}, status_code=200)






def get_ec2_client():
    if platform.system() == "Windows":
        load_dotenv(os.path.join(os.path.dirname(__file__), "tokens.env"))
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        return boto3.client(
            "ec2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="ap-south-1"
        )
    else:
        return boto3.client("ec2", region_name="ap-south-1")

def get_instance_id_by_name(ec2_client, name):
    try:
        response = ec2_client.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [name]}]
        )
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                return instance["InstanceId"]
    except ClientError as e:
        print(f"Error: {e}")
    return None

def start_tradingdatahandling_instance():
    ec2_client = get_ec2_client()
    instance_id = get_instance_id_by_name(ec2_client, "tradingdatahandling")
    if instance_id:
        try:
            ec2_client.start_instances(InstanceIds=[instance_id])
            print(f"Started instance {instance_id}")
        except ClientError as e:
            print(f"Error: {e}")
    else:
        print("Instance not found.")

def get_tradingdatahandling_ip():
    ec2_client = get_ec2_client()
    try:
        response = ec2_client.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": ["tradingdatahandling"]}, {"Name": "instance-state-name", "Values": ["running"]}]
        )
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                return instance.get("PublicIpAddress")
    except ClientError as e:
        print(f"Error: {e}")
    return None


def instancestatus():
    ec2_client = get_ec2_client()
    try:
        response = ec2_client.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": ["tradingdatahandling"]}]
        )
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                state = instance.get("State", {}).get("Name")
                return state  # 'running', 'stopped', etc.
    except ClientError as e:
        print(f"Error: {e}")
    return None

def stop_tradingdatahandling_instance():
    ec2_client = get_ec2_client()
    instance_id = get_instance_id_by_name(ec2_client, "tradingdatahandling")
    if instance_id:
        try:
            ec2_client.stop_instances(InstanceIds=[instance_id])
            print(f"Stopped instance {instance_id}")
        except ClientError as e:
            print(f"Error: {e}")
    else:
        print("Instance not found.")
