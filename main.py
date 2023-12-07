import time

import requests
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from sys import platform

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


def get_data_selenium(selenium_url, headless=False):
    options = Options()
    driver_service = None
    if headless:
        options.add_argument("--headless")
    if platform == "linux" or platform == "linux2":
        driver_service = Service(r'/snap/bin/geckodriver')  # for linux systems
    elif platform == "win32" or platform == "win64":
        driver_service = Service()  # for Windows systems
    browser = webdriver.Firefox(service=driver_service, options=options)

    try:
        browser.get(selenium_url)
    except TimeoutError as time_out_error:
        print(f"{time_out_error}\nURL: {selenium_url}\n")
    except selenium.common.exceptions.TimeoutException as time_out_exception:
        print(f"{time_out_exception}\nURL: {selenium_url}\n")
    except selenium.common.exceptions.NoSuchWindowException as window_exception:
        print(f"{window_exception}URL: {selenium_url}\n")
    except selenium.common.exceptions.WebDriverExceptoin as webdriver_exception:
        print(f"{webdriver_exception}URL: {selenium_url}\n")
    else:
        if "404" in browser.title:
            browser.close()
            return "404"
        else:
            html = browser.page_source
            browser.close()
            return html


def get_all_a_href_from_scrapping(page_document):
    iqc_soup = BeautifulSoup(page_document, "lxml")
    a_href_element = iqc_soup.find_all('a', href=True)
    return [link['href'] for link in a_href_element]


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


def corrupted_links_search(links_list: list, start_from: int = 0, visited_links_list=None) -> None:
    """

    Returns
    -------
    No return
    """
    if visited_links_list is None:
        visited_links_list = []
    for link_level1 in links_list[start_from::]:
        page = get_data_selenium(link_level1, True)
        new_link_level1 = f"{link_level1}\n"
        print(f"A validar a página {link_level1}")
        
        if page == "404":
            with open("corrupted-links.txt", mode='a') as corrupt_file:
                corrupt_file.writelines(f"{links_list.index(link_level1)}:{link_level1}\n")
            visited_links_list.append(link_level1)
        
        elif new_link_level1 not in visited_links_list:
            href_list_level2 = get_all_a_href_from_scrapping(page)
            for link_level2 in href_list_level2:
                if len(link_level2) > 1 and link_level2[0] == "/" and ("/./" not in link_level2):
                    new_link_level2 = f"https://iqc.pt{link_level2}\n"
                    if new_link_level2 not in visited_links_list:
                        print(f"A validar link: {new_link_level2} da página {link_level1}")
                        page_level2 = get_data_selenium(new_link_level2.strip("\n"), True)
                        visited_links_list.append(new_link_level2)

                        if page_level2 == "404":
                            with open("corrupted-links.txt", mode='a') as corrupt_file:
                                corrupt_file.writelines(f'{links_list.index(link_level1)}:{link_level1} - '
                                                        f'{href_list_level2.index(link_level2)}:{new_link_level2}')
                        else:
                            print(f"Link {new_link_level2} da página {link_level1} - OK")
                            with open("visited_links.txt", mode="a") as visited_file:
                                visited_file.writelines(f"{new_link_level2}")
            visited_links_list.append(link_level1)
            print(f"Page from main links ok.\n{link_level1}")
        
        with open("visited_links.txt", mode="a") as visited_file:
            visited_file.writelines(f"{link_level1}\n")
            # visited_file.writelines(page_level2)
            # links_to_write =
    print("Search done.\nPlease verify the files visited_links.txt and corrupted-links.txt")

    # with open("visited_links_list.txt", mode="a") as visited_file:
    #     for page in visited_links_list:
    #         visited_file.writelines(f"{page}\n")


def get_links_from_iqc_txt():
    try:
        with open("all_iqc_links.txt", mode="r") as file_link:
            iqc_all_links = file_link.readlines()
    except FileNotFoundError:
        get_all_links_iqc()
    else:
        return iqc_all_links


if __name__ == "__main__":
    try:
        with open("visited_links.txt", mode="r") as visited_file_link:
            visited_iqc_links = visited_file_link.readlines()
    except FileNotFoundError:
        links_stripped = [link.strip("\n") for link in get_links_from_iqc_txt()]
        corrupted_links_search(links_stripped, 37)
    else:
        not_visited_links_stripped = [link.strip("\n") for link in get_links_from_iqc_txt() if
                                      link not in visited_iqc_links]
        # print(visited_iqc_links)
        corrupted_links_search(not_visited_links_stripped, visited_links_list=visited_iqc_links)
        """
        # print(get_data_selenium("https://iqc.pt/edificacao/122-comentarios/velho-testamento/1-samuel"))
        # print(get_data_selenium("https://iqc.pt/videos/12734-mensagem-proferida-domingo-07-de-maio-2017-por-jose"
        #                        "-ca-r-v-a-lh-os-s-ss-s--"))
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
