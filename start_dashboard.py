import os
import webbrowser
from time import sleep

def start_server():
    """Start the Flask server."""
    os.system("python app.py")

def open_browser():
    """Open the dashboard in Microsoft Edge."""
    sleep(2)  # Wait for the server to start
    webbrowser.get("windows-default").open("http://127.0.0.1:5000")

if __name__ == "__main__":
    start_server()
    open_browser()
