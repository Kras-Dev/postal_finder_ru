# clients/api_client.py

import requests
from utils.custom_logger import CustomLogger

custom_logger = CustomLogger(__name__)

def get_postal_data(post_code):
    url = f"https://api.zippopotam.us/RU/{post_code}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        custom_logger.log_with_context(f"Error fetching data from API: {e}")
        return None