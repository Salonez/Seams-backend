import requests
from src.config import url

def clear():
    requests.delete(
        url + '/clear/v1',
        json={}
    )
