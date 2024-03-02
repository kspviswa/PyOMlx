import requests
import json

url = 'http://127.0.0.1:5000/serve'
#data = {'model': 'stablelm-2-zephyr-1_6b-4bit', 'prompt': 'write a c++ program to sort', 'temp' : 0.3}
data = {'model': 'quantized-gemma-7b-it', 'prompt': 'Hi, tell me a joke', 'temp' : 0.3}
response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})

# If you want to print the response
print(response.status_code)
print(response.text)
