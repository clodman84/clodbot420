import requests

def Shake(txt):
    response = requests.get('https://api.funtranslations.com/translate/shakespeare.json', params={"text": txt})
    if response.status_code == 200:
        output = response.json()['contents']['translated']
    else:
        output = "You guys fucking talk so much"
    return output
print(Shake(input()))