import json

from boundaries.carwale_boundary import get_car_info as get_car_info_from_carwale

def get_car_information(maker_name: str, model_name: str):
    result = get_car_info_from_carwale(maker_name, model_name)
    with open(f'./data/{maker_name}__{model_name}.json', 'w') as file:
        file.write(json.dumps(result))
    print("SUccessful")

get_car_information('mg', 'hector')