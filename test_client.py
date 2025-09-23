import requests

def test_api_devices():
    url = "http://localhost:5000/api/devices"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_api_devices()
