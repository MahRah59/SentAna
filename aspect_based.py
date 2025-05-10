import requests
from bs4 import BeautifulSoup

url = "https://www.svt.se/nyheter/"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Hämta alla nyhetsrubriker
    headlines = soup.find_all("h2", class_="nyh__headline")  # Justera klassen beroende på HTML-strukturen
    
    for h in headlines:
        print(h.get_text(strip=True))
else:
    print("Kunde inte hämta sidan.")