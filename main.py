import requests
from bs4 import BeautifulSoup

URL = "https://iqc.pt/component/osmap/?view=xml&id=1&format=xml"
URL2 = "https://iqc.pt/component/osmap/?view=html&id=1"

headers = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/119.0.6045.109 Mobile/15E148 Safari/604.1",
  "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
  "Accept-Encoding":"gzip, deflate, br",
  "Content-Type":"application/x-www-form-urlencoded",
           "X-Forwarded-Proto": "https",
  "Cookie": "_ga=GA1.2.1637884771.1700409054" }

def get_data(url, headers):
    """
    Get data from the URL and return a beautiful soup object
    """
    response = requests.get(url, headers)
    soup = BeautifulSoup(response.content, "lxml")
    return soup

if __name__ == "__main__":
  #soup = get_data("Site-map.html", headers)
  #print(soup)
  #response = requests.post(URL2, headers)
  #print(response.status_code)
  with open("Site-map.html") as file:
    site_map_html = file.read()

  soup = BeautifulSoup(site_map_html, "lxml")
  tbody = soup.find_all('a', href=True)
  #tbody_childs = [child.name for child in tbody.children]
  print(len(tbody))