import os
import platform
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

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
