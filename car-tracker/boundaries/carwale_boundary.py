import requests

domain = 'https://www.carwale.com/api'

def get_car_info(maker_name: str, model_name: str):
    api_url = f"{domain}/modelpagedata/"
    # api_url = 'https://www.carwale.com/api/modelpagedata/?makeMaskingName=mg&modelMaskingName=hector&cityId=246&areaId=-1&showOfferUpfront=false&platformId=1'

    # Define query parameters as a dictionary
    params = {
        "makeMaskingName": maker_name,
        "modelMaskingName": model_name
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        print("\nGET Request with Parameters Successful!")
        print("Request URL:", response.url) # Shows the constructed URL with parameters
        print("Response JSON (filtered by userId and id):")
        # print(data)
        return data

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        raise e
