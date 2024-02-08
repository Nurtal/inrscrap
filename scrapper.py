import re
from bs4 import BeautifulSoup
from selenium import webdriver


def scrap(target_id):
    """ """

    # parameters
    target_url = f"https://www.inrs.fr/publications/bdd/fichetox/fiche.html?refINRS=FICHETOX_{target_id}"
    driver_path = "/home/bran/drivers/geckodriver"

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox(executable_path=driver_path)

    # Navigate to the target web page
    driver.get(target_url)

    # Get the source code of the web page
    page_source = driver.page_source

    # TODO catch the link to the pdf
    m = re.match('(class="boutonImportant orange")', page_source)
    if m:
        print(m.group(0))
    # print(page_source)


if __name__ == "__main__":

    # parameters
    t = "328"

    # test function
    scrap(t)
