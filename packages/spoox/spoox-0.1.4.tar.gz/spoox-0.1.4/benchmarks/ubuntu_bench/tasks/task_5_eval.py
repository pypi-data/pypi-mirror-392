import sys
import time
import requests

if __name__ == "__main__":

    # give server time to start
    time.sleep(4)

    # try to connect to localhost:3000 and fetch "Hello world"
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code != 200 or "hello world" not in response.text.lower():
            sys.exit("Server did not return expected content.")

    except Exception as e:
        sys.exit(f"Connecting to server failed.")

    sys.exit(0)
