import requests
url = "http://api.open-notify.org/astros.json"
response = requests.request("GET", url)
A = response.json()
people = A['people']
text = ""
for i in people:
    text += str(i)+'\n'
number = A['number']
print('There are currently '+ str(number) + ' people in space\n'+text)
