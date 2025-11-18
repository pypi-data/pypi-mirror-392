import uvicorn

# Import the FastAPI application object
from pwrstat.main import app


def run_server():
    """
    Runs the uvicorn server with the default configuration (host 0.0.0.0, port 8000).

    This function is the entry point defined in pyproject.toml, allowing the
    application to be run simply by calling the installed script name.
    """
    print("Starting CyberPower UPS Status API on http://0.0.0.0:8000")

    # We use uvicorn.run() to start the server programmatically.
    # The first argument is the application import path string.
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        # Set reload=True for development, False for production installs
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
