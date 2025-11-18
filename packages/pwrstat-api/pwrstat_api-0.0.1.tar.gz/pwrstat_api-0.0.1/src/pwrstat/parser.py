import re
import subprocess
from typing import Optional
from pydantic import BaseModel


class UPSProperties(BaseModel):
    """Model for UPS properties data"""

    Model_Name: Optional[str] = None
    Firmware_Number: Optional[str] = None
    Rating_Voltage: Optional[str] = None
    Rating_Power: Optional[str] = None


class UPSStatus(BaseModel):
    """Model for UPS status data"""

    State: Optional[str] = None
    Power_Supply_by: Optional[str] = None
    Utility_Voltage: Optional[str] = None
    Output_Voltage: Optional[str] = None
    Battery_Capacity: Optional[str] = None
    Remaining_Runtime: Optional[str] = None
    Load: Optional[str] = None
    Line_Interaction: Optional[str] = None
    Test_Result: Optional[str] = None
    Last_Power_Event: Optional[str] = None


class UPSData(BaseModel):
    """Combined model for all UPS data"""

    properties: UPSProperties
    status: UPSStatus


def parse_pwrstat_output(output: str) -> UPSData:
    """
    Parse the output of the 'pwrstat -status' command and return a structured
    UPSData object with properties and status information.

    Args:
        output (str): The output string from the 'pwrstat -status' command

    Returns:
        UPSData: A Pydantic model containing 'properties' and 'status' objects
    """
    properties_pattern = r"Properties:(.*?)Current UPS status:"
    status_pattern = r"Current UPS status:(.*?)$"

    properties_match = re.search(properties_pattern, output, re.DOTALL)
    status_match = re.search(status_pattern, output, re.DOTALL)

    properties_dict = {}
    status_dict = {}

    if properties_match:
        properties_text = properties_match.group(1).strip()
        for line in properties_text.split("\n"):
            line = line.strip()
            if line:
                key_value = re.match(r"(.*?)\.+\s+(.*)", line)
                if key_value:
                    key, value = key_value.groups()
                    key = key.strip().replace(" ", "_")
                    properties_dict[key] = value.strip()

    if status_match:
        status_text = status_match.group(1).strip()
        for line in status_text.split("\n"):
            line = line.strip()
            if line:
                key_value = re.match(r"(.*?)\.+\s+(.*)", line)
                if key_value:
                    key, value = key_value.groups()
                    key = key.strip().replace(" ", "_")
                    status_dict[key] = value.strip()

    ups_data = UPSData(
        properties=UPSProperties(**properties_dict), status=UPSStatus(**status_dict)
    )

    return ups_data


def get_ups_data() -> UPSData:
    """
    Executes the 'pwrstat -status' command and returns the parsed data.
    """
    try:
        # Execute the command
        pwrstat_output = subprocess.check_output(
            "sudo pwrstat -status", shell=True, text=True
        )
        # Parse and return the data
        return parse_pwrstat_output(pwrstat_output)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # In case of an error (e.g., command not found), return empty data
        print(f"Error executing pwrstat command: {e}")
        return UPSData(properties=UPSProperties(), status=UPSStatus())
