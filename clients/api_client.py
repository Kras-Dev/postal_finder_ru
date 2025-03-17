import requests


def get_postal_data(country_abbreviation, post_code):
    url = f"https://api.zippopotam.us/{country_abbreviation}/{post_code}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None
