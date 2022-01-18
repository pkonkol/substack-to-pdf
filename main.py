import requests
from bs4 import BeautifulSoup

url = "https://graymirror.substack.com/"

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
print(response.content)