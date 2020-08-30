from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from config import home_directory
import time


def screenshot():

    print("Getting screenshot")
    date = datetime.now().strftime("%Y-%m-%d %H%M")
    print(date)

    # your executable path is wherever you saved the webdriver
    chromedriver = home_directory + "chromedriver"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--window-size=1080,720")

    # url = "https://www.purpleair.com/gmap?&zoom=14&lat=41.81975202373814&lng=-87.67791305733986&clustersize=23&orderby=L&latr=0.04471152946594259&lngr=0.12359619140625"
    # url = "https://www.purpleair.com/map?#13.58/41.81881/-87.67469"
    url = 'https://www.purpleair.com/map?#12.04/41.7969/-87.68273'

    browser = webdriver.Chrome(executable_path=chromedriver, options=options)
    browser.get(url)

    WebDriverWait(browser, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    time.sleep(15)

    # Accept the cookies
    try:
        browser.find_element_by_css_selector('#gdpr-cookie-accept').click()
    except:
        print("no need to accept cookie")

    time.sleep(1)

    # Close the legend
    try:
        browser.find_element_by_css_selector('#paLegendHide').click()
    except:
        print("Unable to close legend")

    filepath = home_directory + 'screenshots/'
    filename = 'sws-air-network ' + date + '.png'

    browser.save_screenshot(filepath + filename)
    browser.quit()

    return filepath + filename