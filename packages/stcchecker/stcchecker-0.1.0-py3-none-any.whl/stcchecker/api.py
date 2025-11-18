import requests

BASE_URL = "http://91.108.184.15:5050/stc?url={url}&cc={cc}"

class STCError(Exception):
    pass

def check(url: str, cc: str):
    """
    Perform STC check using remote API.
    """
    try:
        api_url = BASE_URL.format(url=url, cc=cc)
        response = requests.get(api_url, timeout=30)

        if response.status_code != 200:
            raise STCError(f"API error: {response.status_code}")

        return response.json()

    except Exception as e:
        raise STCError(str(e))