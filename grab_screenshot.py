from selenium import webdriver
from datetime import datetime
from PIL import Image
from io import BytesIO
import time

def screenshot():

    date = datetime.now().strftime("%Y-%m-%d %H%M")
    print(date)

    # your executable path is wherever you saved the gecko webdriver
    geckodriver = "/usr/local/bin/geckodriver"
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    url = "https://www.purpleair.com/gmap?&zoom=14&lat=41.81975202373814&lng=-87.67791305733986&clustersize=23&orderby=L&latr=0.04471152946594259&lngr=0.12359619140625"

    browser = webdriver.Firefox(executable_path=geckodriver, options=options)

    browser.get(url)
    time.sleep(10)

    browser.find_element_by_css_selector('#gdpr-cookie-accept').click()


    browser.save_screenshot('screenshot.png')
    browser.quit()

    im = Image.open('screenshot.png') # uses PIL library to open image in memory

    location = {
        'x': 315,
        'y': 91
    }

    size = {
        'width': 750,
        'height': 535
    }

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']


    filepath = './screenshots/'
    filename = 'sws-air-network ' + date + '.png'

    im = im.crop((left, top, right, bottom)) # defines crop points
    im.save(filepath + filename) # saves new cropped image

    return filepath + filename
