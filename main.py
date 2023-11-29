import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

URL = "https://iqc.pt/component/osmap/?view=xml&id=1&format=xml"
URL2 = "https://iqc.pt/component/osmap/?view=html&id=1"

headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (HTML, like Gecko) "
                  "CriOS/119.0.6045.109 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Forwarded-Proto": "https",
    "Cookie": "_ga=GA1.2.1637884771.1700409054"}


def get_data(url, browser_headers, features):
    """
    Get data from the URL and return a beautiful soup object
    """
    response_data = requests.get(url, browser_headers)
    soup_response = BeautifulSoup(response_data.content, features)
    return soup_response


def get_data_selenium(selenium_url):
    options = Options()
    driver_service = Service(r'/snap/bin/geckodriver')
    browser = webdriver.Firefox(service=driver_service, options=options)

    browser.get(selenium_url)
    if "404" in browser.title:
        browser.close()
        return "404"
    else:
        html = browser.page_source
        browser.close()
        return html


def get_all_a_href_from_scrapping(page):
    iqc_soup = BeautifulSoup(page, "lxml")
    tbody = iqc_soup.find_all('a', href=True)
    return [link['href'] for link in tbody]


def get_all_links_iqc():
    try:
        with open("site-map-xml.hml", mode='r') as xml_file:
            site_map_xml = xml_file.read()
    except FileNotFoundError:
        html = get_data_selenium(URL)
        time.sleep(3)
        with open("site-map-xml.hml", mode='w') as xml_file:
            for line in html:
                xml_file.write(line)
        get_all_links_iqc()
    else:
        href_list = get_all_a_href_from_scrapping(site_map_xml)
        with open("all_iqc_links.txt", mode="w") as link_file:
            for href_link in href_list:
                link_file.writelines(f"{href_link}\n")
        print(href_list)


if __name__ == "__main__":
    try:
        with open("all_iqc_links.txt", mode="r") as file_link:
            iqc_all_links = file_link.readlines()
    except FileNotFoundError:
        get_all_links_iqc()
    else:
        print(type(iqc_all_links))
        links_stripped = [link.strip("\n") for link in iqc_all_links]
        #print(get_data_selenium("https://iqc.pt/edificacao/122-comentarios/velho-testamento/1-samuel"))
        #print(get_data_selenium("https://iqc.pt/videos/12734-mensagem-proferida-domingo-07-de-maio-2017-por-jose"
        #                        "-carvalho"))
        for link_level1 in links_stripped:
            page = get_data_selenium(link_level1)
            if page == "404":
                with open("site-map-xml.hml", mode='a') as corrupt_file:
                    corrupt_file.write(f"{links_stripped.index(link_level1)}:{link_level1}")
            else:
                href_list_level2 = get_all_a_href_from_scrapping(page)
                for link_level2 in href_list_level2:
                    page_level2 = get_data_selenium(link_level2)
                    if page_level2 == "404":
                        with open("site-map-xml.hml", mode='a') as corrupt_file:
                            corrupt_file.write(f"{links_stripped.index(link_level1)}:{link_level1} - "
                                               f"{href_list_level2.index(link_level2)}:{link_level2}")

        """
        #response = requests.get("https://iqc.pt/videos", headers)
        #print(response.status_code)
        options = Options()
        driver_service = Service(r'/snap/bin/geckodriver')
        browser = webdriver.Firefox(service=driver_service, options=options)

        browser.get('https://iqc.pt/edificacao/122-comentarios/velho-testamento/1-samuel')
        page = "https://iqc.pt/edificacao/122-comentarios/velho-testamento/1-samuel"
        js = '''
        let callback = arguments[0];
        let xhr = new XMLHttpRequest();
        xhr.open('GET','''
        f"{page}"
        ''', true);
        xhr.onload = function () {
            if (this.readyState === 4) {
                callback(this.status);
            }
        };
        xhr.onerror = function () {
            callback('error');
        };
        xhr.send(null);
        '''

        status_code = browser.execute_async_script(js)
        print(status_code)
        browser.close()
        """
