import requests

url = "https://proxy-orbit1.p.rapidapi.com/v1/"

querystring = {"protocols":"http"}

headers = {
    'x-rapidapi-key': "361af19b9fmsh14fe3b953cc840ap175819jsn96f4b089df57",
    'x-rapidapi-host': "proxy-orbit1.p.rapidapi.com"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)