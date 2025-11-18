from fastapi import FastAPI
from pwrstat.parser import get_ups_data, UPSData

app = FastAPI(
    title="CyberPower UPS Status API",
    description="An API to get the status of a CyberPower UPS using the pwrstat utility.",
    version="1.0.0",
)


@app.get("/status", response_model=UPSData)
async def get_status():
    """
    Retrieves the current status of the UPS.

    This endpoint executes the `pwrstat -status` command on the host machine
    and returns the parsed output in a JSON format.
    """
    ups_data = get_ups_data()
    return ups_data


@app.get("/")
async def root():
    """
    Root endpoint with a welcome message.
    """
    return {
        "message": "Welcome to the UPS Status API. Go to /status to get the current UPS data, or /docs for the API documentation."
    }
