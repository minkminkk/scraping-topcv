import requests
from time import sleep


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko)  \
        Chrome/91.0.4472.124 Safari/537.36"
}


def send_request(
    method: str, 
    url: str, 
    headers: dict = HEADERS,
    retries: int = 3,
    retry_delay: int = 10
):
    """
    Function for sending requests, with response validation and retries
    when failed due to rate limits.

    Argument:
        method [str]: HTTP method for the requests (e.g. get, post...).
        url [str]: URL to which the request is sent.
        headers [str]: The request headers (defaults to HEADERS).
        retries [int]: Number of retries if rate limited (defaults to 3).
        retry_delay [int]: Seconds between retries (defaults to 10).

    Raises exception when response status code is not 200.
    """
    response = requests.request(method, url, headers = headers)

    # Status code handling
    if response.status_code != 200:
        # Retry only if request rate limited
        if response.status_code == 429:
            if retries <= 0:
                raise Exception("Too many requests \
sent to server. Try again later. (Status code 429)")
            
            print("Request rate limited. Sending another request" \
                + f"in {retry_delay} seconds.")
            sleep(retry_delay)
            send_request(method, url, headers, retries - 1, retry_delay)
        else:
            response.raise_for_status()

    return response