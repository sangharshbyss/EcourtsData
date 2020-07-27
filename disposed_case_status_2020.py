"""file only targets one district in one state
scrapy can be used to go to multipule states and multiple districts
after grabing (with "response.join") url it can be passed to selenium as
rest of the pages are js loaded."""
import base64
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
from PIL import Image
from io import BytesIO
import cv2
from pytesseract import pytesseract
from selenium.common.exceptions import NoSuchElementException, TimeoutException, \
    WebDriverException
import check_the_act
from ecourts_logging import logger
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


#set chrome options for automatic download without popup.
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument('--proxy-server=103.75.226.25:59598')
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option('prefs',  {
    "download.default_directory":
        '/home/sangharshmanuski/EcourtsData/disposed_off/pune3/orders',
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
    }
)

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

# constants
URL = r'https://districts.ecourts.gov.in/pune'

main_Directory = r'/home/sangharshmanuski/EcourtsData/disposed_off/pune3'
orders_directory = r'/home/sangharshmanuski/EcourtsData/disposed_off/pune3/orders'


#options.add_argument("--headless")
#options.add_argument("--private-window")




combo_identifier = '#sateist'
wait = WebDriverWait(driver, 180)
waitShort = WebDriverWait(driver, 3)


# FUNCTIONS

def wait_for_page_load(element, elementCSS):
    # 1. wait for stalness of element 2. wait until visibility of that element with CSS)
    wait.until(EC.staleness_of(element))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, elementCSS)))


def by_case_status():
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                    'button.accordion2:nth-child(2)'))).click()
    wait.until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            'div.right-accordian:nth-child(1) > div:nth-child(3) '
            '> ul:nth-child(1)> li:nth-child(7) > a:nth-child(1)'))).click()

def court_complex_list():
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#court_complex_code')))
    complex_combo = Select(driver.find_element_by_css_selector('#court_complex_code'))
    # return list of non-empty values from combo box
    court_complex_names = [o.get_attribute("text")
                           for o in complex_combo.options if o.get_attribute("value") != '0']
    court_complex_values = [o.get_attribute("value")
                            for o in complex_combo.options if o.get_attribute("value") != '0']

    return court_complex_names, court_complex_values


def single_court_complex(complex_number, value_complex_list=None, name_complex_list=None):
    # returns single court complex name and value of the same
    complex_combo = Select(driver.find_element_by_css_selector('#court_complex_code'))
    value_complex = value_complex_list[complex_number]
    name_complex = name_complex_list[complex_number]
    complex_combo.select_by_value(value_complex)
    logger.info(f'\n {name_complex} selected. checking for records')
    logger.debug(f'{name_complex}')
    return name_complex


def select_act(some_name_complex=None, i=0):
    """Populates list of acts.
    if the list is empty it waits for a 1 sec and tries again
    after trying 10 times it closes the effort and returns"""

    acts = Select(driver.find_element_by_css_selector('#case_type'))
    act_list = acts.options
    second = 0
    while len(act_list) < 2:
        if second < 7:
            time.sleep(1)
            second += 1

        else:

            return False
    else:
        acts.select_by_value('36')

        return True


def input_year(any_year):
    year = driver.find_element_by_css_selector('#search_year')
    year.send_keys(any_year)


def accept_alert(tab=None):
    try:
        waitShort.until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        driver.switch_to.window(tab)

        return True
    except (NoSuchElementException, TimeoutException):

        return False


def wait_msg():
    try:
        please_wait = driver.find_element_by_css_selector('#waitmsg')
        if please_wait.is_displayed():

            return True
        else:

            return False
    except NoSuchElementException:

        return False


def wait_msg_wait():
    # wait for wait msg to disappear only for 5 sec
    # in case of alert wait msg remains for ever so waiting only for 5 sec is imp
    sleep = 1
    while wait_msg():
        if sleep < 6:
            time.sleep(sleep)
            sleep += 1
            continue
        else:

            break

    return


def invalid_captcha():
    # if captcha is invalid it returns true.
    try:
        incorrect = driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').text
        in_valid_captcha = "Invalid Captcha"
        if incorrect == in_valid_captcha:

            return True
        else:

            return False
    except NoSuchElementException:

        return False


def no_record_found(courtcomplex=None):
    # checks if no record found message is displayed

    try:
        no_record = driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').text
        no_record_available = "Record Not Found"
        if no_record == no_record_available:
            return True

    except NoSuchElementException:

        return False


def captcha_to_text():
    # captures the captcha image
    elem = driver.find_element_by_id("captcha_image")
    loc = elem.location
    size = elem.size
    left = loc['x']
    top = loc['y']
    width = size['width']
    height = size['height']
    box = (int(left), int(top), int(left + width), int(top + height))
    screenshot = driver.get_screenshot_as_base64()
    img = Image.open(BytesIO(base64.b64decode(screenshot)))
    area = img.crop(box)

    area.save(os.path.join(main_Directory, 'file_trial.png'), 'PNG')
    img = cv2.imread(os.path.join(main_Directory, 'file_trial.png'), 0)
    ret, thresh1 = cv2.threshold(img, 111, 255, cv2.THRESH_BINARY)
    cv2.imwrite(os.path.join(main_Directory, 'oneDisNoLoop.png'), thresh1)
    # know the text with pytesseract
    captcha_text = pytesseract.image_to_string(
        Image.open(os.path.join(main_Directory, 'oneDisNoLoop.png')))
    return captcha_text


def submit_form():
    # "enters captcha text taken from crack_captcha(..) function"
    captcha = driver.find_element_by_id('captcha')
    captcha.send_keys(captcha_to_text())
    driver.find_element_by_css_selector('input.button:nth-child(1)').click()


def view(directory, some_complex=None):
    logger.info(f'{some_complex}')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'a.someclass')))
    list_all_view = driver.find_elements_by_css_selector(
        'a.someclass')

    for single in range(len(list_all_view)):
        try:
            list_all_view[single].click()
            wait.until(EC.presence_of_element_located((By.ID, 'back_top')))
            time.sleep(3)
            open_file = open(
                os.path.join(directory, f'case_info{single}.html'), "w")
            open_file.write(driver.page_source)
            open_file.close()
            if check_the_act.act_check(driver):
                download_order(directory)
            back = driver.find_element_by_id('back_top')
            back.click()

        except TimeoutException:
            logger.info(f'{TimeoutException}. trying again')
            time.sleep(5)
            if back := driver.find_element_by_id('back_top').is_displayed():
                back.click()
            continue
        except WebDriverException:
            logger.info(f'{WebDriverException}. \n breaking out with False')
            time.sleep(5)
            if back := driver.find_element_by_id('back_top').is_displayed():
                back.click()
            continue

    logger.info(f'{some_complex} downloaded')






def download_order(dir):
    try:
        if driver.find_element_by_css_selector('.blinking').is_displayed():
            logger.info('order not upladed yet')
            return
    except:
        logger.info('order available')
    else:
        logger.info('available')
    orders = driver.find_elements_by_xpath('//table[@class="order_table"]//td/a')
    if orders is not None:
        for order in range(len(orders)):
            new_current_window = driver.current_window_handle
            orders[order].click()
            wait.until(EC.number_of_windows_to_be(3))
            driver.switch_to.window(driver.window_handles[-1])
            logger.info("downloading...")

            try:
                driver.find_element_by_css_selector('#download').click()
                driver.close()
                logger.info('tab clsoed')
                driver.switch_to.window(new_current_window)
                logger.info('tab shift')
            except:
                logger.info('no file')
                driver.close()
                logger.info('tab close')
                driver.switch_to.window(new_current_window)
                logger.info('tab shifted. no file was uploaded')
        return logger.info(f'number of orders downloaded: {len(orders)}')
    else:
        logger.info('entire order table was missing and no blinking text')
        return



def dist_dir(some_district_name=None):
    district_directory = os.path.join(
        main_Directory, some_district_name)  # create new
    if not os.path.exists(district_directory):  # if not directory exists, create one
        os.mkdir(district_directory)
        logger.info(f'directory for {some_district_name} created')

    return district_directory


def court_complex_dir(name_complex):
    # makes separate directory particular court complex
    court_complex_directory = os.path.join(
        main_Directory, name_complex)  # create new
    if not os.path.exists(court_complex_directory):  # if not directory exists, create one
        os.mkdir(court_complex_directory)

    else:

        pass
    return court_complex_directory


# MAIN CODE

# load the main page
driver.get(URL)
# variable for current tab. Easy to return to this tab.
current = driver.window_handles[0]
by_case_status()
wait.until(EC.number_of_windows_to_be(2))
# define new tab by differentiating from current tab.
newWindow = [window for window in driver.window_handles if window != current][0]
# 2.4.a
# switch to the new tab. ref:
# https://stackoverflow.com/questions/41571217
# /python-3-5-selenium-how-to-handle-a-new-window-and-wait-until-it-is-fully-lo
driver.switch_to.window(newWindow)
# 2.4.b new object from Formfilling(districtCourt)
this_name_complex_list, this_value_complex_list = court_complex_list()

# 2.4.c loop over all complexes
i = 5
while i < len(this_name_complex_list) :
    try:

        # 2.4.1.1 select court complex
        this_name_complex = single_court_complex(i,
                                                 this_value_complex_list,
                                                 this_name_complex_list)
        # 2.4.1.2 select act.
        # If the acts are not available go to the next court complex
        # or if option for particular act is not present go to next court complex
        if not select_act(this_name_complex, i=i):
            logger.info(f'no act found {this_name_complex}')
            continue
        input_year("2020")
        driver.find_element_by_css_selector('#search_year').click()
        driver.find_element_by_css_selector('#radD').click()
        while True:
            submit_form()
            time.sleep(1)
            if accept_alert(newWindow):
                driver.find_element_by_css_selector('#captcha_container_2 '
                                                    '> div:nth-child(1) > div:nth-child(1) '
                                                    '> span:nth-child(3) > a:nth-child(7) '
                                                    '> img:nth-child(1)').click()
                time.sleep(2)

                continue

            if not invalid_captcha():

                break
            else:

                continue

        # 2.4.5 if no record found go the next court complex
        if no_record_found(this_name_complex):
            i += 1
            continue  # skip rest of the code and continue the for loop from start.
        else:
            # 2.4.6 make new directory
            complex_directory = court_complex_dir(this_name_complex)
            # 2.4.7 download all the records
            view(complex_directory, this_name_complex)
            logger.info('downloading')
            i += 1

    except TimeoutException:

        logger.info(f'timeout exception {this_name_complex_list[i]}. missed.')
        continue
    except WebDriverException:

        logger.info(f'webdriver exception {this_name_complex_list[i]}')
        time.sleep(60)

        continue

logger.info(f'all court complexes in pune completed')
driver.close()