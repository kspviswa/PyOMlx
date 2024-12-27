import requests
import json
from openai import OpenAI

#url = 'http://127.0.0.1:5000/serve'
#url = 'http://127.0.0.1:5000/'
#data = {'model': 'stablelm-2-zephyr-1_6b-4bit', 'prompt': 'write a c++ program to sort', 'temp' : 0.3}
#data = {'model': 'phi-2-hf-4bit-mlx', 'prompt': 'Hi, tell me a joke', 'temp' : 0.3}
#response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
#response = requests.get(url)

# If you want to print the response
#print(response.status_code)
#print(response.text)

client = OpenAI(base_url='http://127.0.0.1:11434/v1', api_key='pyomlx')
response = client.chat.completions.create(model="mlx-community/Phi-3-mini-4k-instruct-4bit", 
                                          messages=[{'role':'user', 'content':'how are you?'}])
print(response.choices[0].message.content)