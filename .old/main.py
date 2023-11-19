"""


Hit RUN to see this project in action!

This is a Python script that showcases the scraping capabilities of Python.

It scrapes the current temperature from weather.com and prints it to the console. It keeps doing it every 30 seconds.

Feel free to edit the code to scrape other websites depending on your needs!
"""

import time

import requests
from bs4 import BeautifulSoup

city = "USNY0996:1:US"  # New York city code
city_name = "New York"


def get_temp_tag(tag):
  # this may or may not be still valid; keep in mind
  # that yahoo may change their html layout in the future
  # and thus this script may no longer work; check
  # if the rule below still works in case of errors
  return tag.has_attr('class') and any(
      "CurrentConditions--tempValue--" in str(i) for i in tag['class'])


def fetch_weather(city):
  url = f"https://weather.com/weather/today/l/{city}"
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')
  element = soup.find(get_temp_tag)
  temperature = element.text if element else "not available"
  return temperature


print(
    "Weather script is running."
    f" Will keep checking the current weather in {city_name} every 30 seconds...\n\n"
)

if __name__ == "__main__":
  while True:
    current_temperature = fetch_weather(city)
    print(f"Current temperature in {city_name}: {current_temperature}")
    time.sleep(30)
