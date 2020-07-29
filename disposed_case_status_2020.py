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
import directories_files
from file_append import append_file, append_dict_as_row, open_dictionary_with_headers


profile = webdriver.FirefoxProfile()
orders_directory = r'/home/sangharshmanuski/EcourtsData/disposed_off/pune3/orders'
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.dir", orders_directory)
profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                       "application/msword, application/pdf")
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.manager.focusWhenStarting", False)
profile.set_preference("browser.download.useDownloadDir", True)
profile.set_preference("browser.helperApps.alwaysAsk.force", False)
profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
profile.set_preference("browser.download.manager.closeWhenDone", True)
profile.set_preference("browser.download.manager.showAlertOnComplete", False)
profile.set_preference("browser.download.manager.useWindow", False)
profile.set_preference("services.sync.prefs.sync.browser.download.manager."
                       "showWhenStarting", False)
profile.set_preference("pdfjs.disabled", True)
profile.update_preferences()

driver = webdriver.Firefox(firefox_profile=profile)

# constants
URL = r'https://districts.ecourts.gov.in/pune'

main_Directory = r'/home/sangharshmanuski/EcourtsData/disposed_off/pune3'
summary_directory = os.path.join(main_Directory, 'summary')
combo_identifier = '#sateist'
wait = WebDriverWait(driver, 180)
waitShort = WebDriverWait(driver, 3)


# FUNCTIONS

def wait_for_page_load(element, element_css):
    # 1. wait for stalness of element 2. wait until visibility of that element with CSS)
    wait.until(EC.staleness_of(element))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, element_css)))


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

    return name_complex


def select_act():
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


def no_record_found():
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


def record_found_summary():
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'a.someclass')))
    list_all_view = driver.find_elements_by_css_selector(
        'a.someclass')
    number_of_records = len(list_all_view)
    logger.info(number_of_records)
    return number_of_records


def case_identifier():
    list_all = driver.find_elements_by_xpath(
        '/html/body/form/div[8]/div/div[5]/div/table/tbody/tr/td[2]')
    number_year_text = []
    for number_year in list_all:
        number_year_text.append(number_year.text)
    return number_year_text


def view(some_complex=None):
    logger.info(f'{some_complex}')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'a.someclass')))
    list_all_view = driver.find_elements_by_css_selector(
        'a.someclass')
    number_of_records = len(list_all_view)
    for single in range(number_of_records):
        try:
            list_all_view[single].click()
            wait.until(EC.presence_of_element_located((By.ID, 'back_top')))
            time.sleep(1)
            registration = driver.find_element_by_xpath(
                '/html/body/form/div[6]/div[2]/div[1]/span[4]/label').text
            registration = str(registration).replace("/", "_")
            registration_date = driver.find_element_by_xpath(
                '/html/body/form/div[6]/div[2]/div[1]/span[4]/span[2]/label[2]').text
            page = driver.page_source
            case_details_file = directories_files.district_record_details(
                complex_directory, "pune_cases")
            case_details, headers = open_dictionary_with_headers(page, case_details_file)
            append_dict_as_row(case_details_file, case_details, headers)
            if check_the_act.act_check(driver):
                page = driver.page_source
                poa_case_details = directories_files.district_records_poa(
                    complex_directory, "pune")
                case_details, headers = open_dictionary_with_headers(
                    page, poa_case_details)
                append_dict_as_row(poa_case_details, case_details, headers)
                download_order(registration)
                back = driver.find_element_by_css_selector(
                    "#back_top > center:nth-child(1) > a:nth-child(1)")
                back.click()
                continue
            else:
                back = driver.find_element_by_css_selector(
                    "#back_top > center:nth-child(1) > a:nth-child(1)")
                back.click()
                logger.info(f'{some_complex} downloaded')


        except TimeoutException:
            error_message = f':time_out exception: {single}: {this_name_complex} '
            time.sleep(3)
            if back := \
                    driver.find_element_by_css_selector(
                        "#back_top > center:nth-child(1) "
                        "> a:nth-child(1)").is_displayed():
                back.click()
            continue
        except WebDriverException:
            logger.info(f'{WebDriverException}. \n breaking out with False')
            time.sleep(5)
            error_message = f':time_out exception: {single}: {this_name_complex} '
            if back := \
                    driver.find_element_by_css_selector(
                        "#back_top > center:nth-child(1) "
                        "> a:nth-child(1)").is_displayed():
                back.click()
            continue


def download_order(number="no_number"):
    time.sleep(3)
    try:
        if driver.find_element_by_css_selector('.blinking').is_displayed():
            logger.info('order not upladed yet')
            back = driver.find_element_by_css_selector(
                "#back_top > center:nth-child(1) > a:nth-child(1)")
            back.click()

            return
    except NoSuchElementException:
        logger.info('order available')

    orders = driver.find_elements_by_xpath('//table[@class="order_table"]//td/a')
    if orders is not None:
        for order in range(len(orders)):
            orders[order].click()
            time.sleep(3)
            # driver.switch_to.window(driver.window_handles[-1])
            message_orders_downloaded = f':downloaded {number}_2020_{order}.txt'
            append_file(order_summary, message_orders_downloaded)
            logger.info(f"downloading...{order}")
        logger.info(f'number of orders downloaded: {len(orders)}')
        return
    else:
        no_order_table = f'no order table \n ' \
                         f'{number}_2020'
        append_file(order_summary, no_order_table)
        back = driver.find_element_by_css_selector(
            "#back_top > center:nth-child(1) > a:nth-child(1)")
        back.click()
        logger.info('entire order table was missing and no blinking text')
        return


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
# for now, it is just for Pune. Few things will change while iterating all districts
pune_directory = directories_files.dist_dir(main_Directory, "pune")
pune_summary = directories_files.district_summary(pune_directory, "pune")
message_complex_number = (f':number of complex: {len(this_name_complex_list)}:\n')
append_file(pune_summary, message_complex_number)
for index, value in enumerate(this_name_complex_list):
    message_name_complex = f':{index}  :  {value}\n'
    append_file(pune_summary, message_name_complex)
catch_errors = directories_files.errors_file(pune_directory, 'pune')
# 2.4.c loop over all complexes
i = 0
while i < len(this_name_complex_list):
    try:

        # 2.4.1.1 select court complex
        this_name_complex = single_court_complex(i,
                                                 this_value_complex_list,
                                                 this_name_complex_list)
        # 2.4.1.2 select act.
        # If the acts are not available go to the next court complex
        # or if option for particular act is not present go to next court complex
        logger.info(f"{this_name_complex}")
        if not select_act():
            logger.info(f'no act found {this_name_complex_list[i]}')
            act_message = f':{this_name_complex}:Act Does Not Apply:\n'
            append_file(pune_summary, act_message)
            continue
        input_year("2020")
        logger.info('in year 2020')
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
        if no_record_found():
            not_found = f':{this_name_complex}:Record Not Found:\n'
            append_file(pune_summary, not_found)
            i += 1
            continue  # skip rest of the code and continue the for loop from start.
        else:
            number_records = record_found_summary()
            record_found = f':{this_name_complex}:{number_records}:\n'
            # 2.4.6 make new directory
            complex_directory = directories_files.court_complex_dir(
                main_Directory, this_name_complex)
            complex_summary, order_summary = directories_files.complex_summary(
                complex_directory=complex_directory,
                                              name_of_the_complex=this_name_complex,
                                              registration_number="some number")
            complex_cases_list = case_identifier()
            message_complex_summry = f':      total number of records: ' \
                                     f'        {number_records}         :\n'
            for index, each_case in enumerate(complex_cases_list):
                message_complex_cases = f':{index}  :  {each_case}:\n'
                append_file(complex_summary, message_complex_cases)
            # 2.4.7 download all the records
            view(complex_directory)
            i += 1

    except TimeoutException:
        message_timeout = f':{this_name_complex_list[i]} TimeoutException Error:'
        append_file(catch_errors, message_timeout)
        logger.info(f'timeout exception {this_name_complex_list[i]}. missed.')
        continue
    except WebDriverException:
        message_timeout = f':{this_name_complex_list[i]} TimeoutException Error:'
        append_file(catch_errors, message_timeout)
        logger.info(f'webdriver exception {this_name_complex_list[i]}\n'
                    f'sleeping for 60 secs')
        time.sleep(60)
        continue

logger.info(f'all court complexes in pune completed')
driver.close()
