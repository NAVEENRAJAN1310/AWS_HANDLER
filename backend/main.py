
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ec2_handler import (
    start_tradingdatahandling_instance,
    get_tradingdatahandling_ip,
    stop_tradingdatahandling_instance,
    instancestatus
)

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
