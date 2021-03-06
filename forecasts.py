import requests
from datetime import datetime

BASE_URL = "https://meteo.imgw.pl/api/meteo/messages/v1/burzynki/latest"

def get_all():
    response = requests.get(f'{BASE_URL}/lclist').json()
	
    forecast_len = len(response["forecast"])	
	
    if forecast_len > 0: 
	    for i in range(forecast_len):
    		if i == 0:
    		    response["forecast"][i]["current"] = True
    		else:
    		    response["forecast"][i]["current"] = False
    		
    		response["forecast"][i]["validToTimestamp"] = response["forecast"][i]["validTo"]
    		response["forecast"][i]["dayOrNight"] = get_day_or_night(int(response["forecast"][i]["validFrom"]))

    		response["forecast"][i]["validFrom"] \
    		    = datetime.utcfromtimestamp(int(response["forecast"][i]["validFrom"])).strftime("from %H:%M on %d.%m")

    		response["forecast"][i]["validTo"] \
    		    = datetime.utcfromtimestamp(int(response["forecast"][i]["validTo"])).strftime("to %H:%M on %d.%m")

    		response["forecast"][i]["issuedAt"] \
    		    = datetime.utcfromtimestamp(int(response["forecast"][i]["issuedAt"])).strftime("issued at %H:%M on %d.%m")

    return response

def get_forecast(index: int):
    forecasts = get_all()
    if index >= len(forecasts['forecast']):
        return None
    response = requests.get(f"{BASE_URL}/forecast/{forecasts['forecast'][index]['validToTimestamp']}").json()
    return response

def get_last_imgw_state():
    response = get_all()['monitoring']
    if(len(response)) > 0:
        last_state_timestamp = int(response[-1]['validTo'])
        return requests.get(f"{BASE_URL}/monitoring/{last_state_timestamp}").json()
    return None

def get_all_as_text():
    response = get_all()
    if len(response['forecast']) == 0:
        return None
    message = f"Avaliable Forecasts:\n"
    for i in range(len(response["forecast"])):
        message += f"""({'current' if response['forecast'][i]["current"] else response['forecast'][i]["dayOrNight"]}) \
{response['forecast'][i]["validFrom"]} {response['forecast'][i]["validTo"]}\
{' [/fmap current, /finfo current]' if response['forecast'][i]["current"] else f'[/fmap {i}, /finfo {i}]'}
"""
    return message

def get_day_or_night(timestamp: int):
    hour = datetime.utcfromtimestamp(timestamp).hour
    if hour > 19:
        return "night"
    return "day"
