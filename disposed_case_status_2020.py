"""all well. from disposed_case_status_2020.
as there was mistake in acts sections.
re-downloading records except downloading orders"""

from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
from pytesseract import pytesseract
from selenium.common.exceptions import NoSuchElementException, \
    TimeoutException, WebDriverException
import csv
import base64
import time
import os
import cv2
import sys

from file_append import append_file, append_dict_as_row, write_mode
from case_details import ParseCase, History
from ecourts_logging import logger
import check_the_act
import directories_files

profile = webdriver.FirefoxProfile()
orders_directory = r'/home/sangharshmanuski/Documents/ecourts_bail_disposed/orders'
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
profile.set_preference("network.proxy.type", 1)
profile.set_preference("network.proxy.http","116.202.103.223")
profile.set_preference("network.proxy.http_port", 21869)
profile.update_preferences()

driver = webdriver.Firefox(firefox_profile=profile)

# constants
district_name_here = sys.argv[1]
URL = 'https://districts.ecourts.gov.in/' + district_name_here

main_Directory_name = sys.argv[2]

base_Directory = os.path.join(
    '/home/sangharshmanuski/Documents/ecourts_bail_disposed/',
    main_Directory_name)
main_Directory_name_sub = sys.argv[3]
main_Directory = os.path.join(base_Directory, main_Directory_name_sub)
summary_directory = os.path.join(main_Directory, 'summary')
combo_identifier = '#sateist'
wait = WebDriverWait(driver, 180)
waitShort = WebDriverWait(driver, 3)

ipc = 'indian penal code'
poa = 'prevention of atrocities'
pcso = 'protection of children from sexual'
pcr = 'protection of civil rights'
cpr = 'code of criminal procedure'


# FUNCTIONS

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


def single_court_complex(
        complex_number, value_complex_list=None, name_complex_list=None):
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


def open_dictionary_with_headers(out_file, headers):
    with open(out_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        f.close()


def view(some_complex=None):
    logger.info(f'{some_complex}')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'a.someclass')))
    list_all_view = driver.find_elements_by_css_selector('a.someclass')
    list_all_view_text = driver.find_elements_by_css_selector('.col-xs-2')
    start_lenth = sys.argv[4]
    end_lenth = sys.argv[5] if int(sys.argv[5]) >= int("3") else len(list_all_view)
    for click_here in list_all_view[int(start_lenth):int(end_lenth)]:
        try:
            click_here.click()


        except (WebDriverException,
                TimeoutException,
                NoSuchElementException):
            logger.info(f"something went wrong")
            return
        remaining = len(list_all_view) - list_all_view.index(click_here)
        logger.info(f"{remaining}")

        wait.until(EC.presence_of_element_located((By.ID, 'back_top')))
        time.sleep(2)
        registration = driver.find_element_by_xpath(
            '/html/body/form/div[6]/div[2]/div[1]/span[4]/label').text
        registration = str(registration).replace("/", "_")
        message_processing = f'{registration}'
        append_file(complex_summary, message_processing)
        logger.info(message_processing)
        # create directory for history
        directory_history = directories_files.history_direcotry(complex_directory)
        try:
            if check_the_act.act_check(driver):
                poa_page = driver.page_source
                poa_soup = BS(poa_page, 'lxml')
                poa_case_details = ParseCase(poa_soup, base_dictionary)
                append_dict_as_row(poa_case_details_file,
                                   poa_case_details.set_dictionary(),
                                   fields)
                download_order(registration)
                if driver.find_element_by_css_selector(
                        ".history_table").is_displayed():
                    history_file = os.path.join(directory_history,
                                                 f'history_{registration}.csv')
                    write_mode(history_file)
                    history_record = History(poa_soup, base_dictionary, history_file)
                    history_record.case_history()
                    back = driver.find_element_by_css_selector(
                        "#back_top > center:nth-child(1) > a:nth-child(1)")
                    back.click()
                    logger.info(f'order downloaded {registration}')
                    time.sleep(2)
                    continue
                else:
                    history_file = os.path.join(directory_history,
                                                f'history_{registration}.csv')
                    write_mode(history_file, "order downloaded {registration}. No history displayed")
                back = driver.find_element_by_css_selector(
                    "#back_top > center:nth-child(1) > a:nth-child(1)")
                back.click()

            else:
                page = driver.page_source
                base_soup = BS(page, 'lxml')
                case_details_record = ParseCase(base_soup, base_dictionary)
                append_dict_as_row(
                    case_details_file, case_details_record.set_dictionary(),
                    fields)
                # a seperate file for recording history of case.
                history_file = os.path.join(directory_history,
                                            f'history_{registration}.csv')
                if driver.find_element_by_css_selector(
                        ".history_table").is_displayed():
                    write_mode(history_file)
                    history_record = History(base_soup,
                                             base_dictionary, history_file)
                    history_record.case_history()
                    back = driver.find_element_by_id('back_top')
                    back.click()
                    logger.info(f'{this_name_complex} downloaded but no PoA')
                    time.sleep(2)
                    continue
                else:
                    back = driver.find_element_by_id("back_top")
                    back.click()
        except WebDriverException:
            back = driver.find_element_by_id("back_top")
            back.click()


def download_order(number="no_number"):
    time.sleep(3)
    try:
        if driver.find_element_by_css_selector('.blinking').is_displayed():
            logger.info('order not upladed yet')
            return
    except NoSuchElementException:
        logger.info('order available')

    orders = driver.find_elements_by_xpath(
        '//table[@class="order_table"]//td/a')
    if orders is not None:
        for order in range(len(orders)):
            orders[order].click()
            time.sleep(3)
            # driver.switch_to.window(driver.window_handles[-1])
            message_orders_downloaded = f':downloaded {number}_2020_{order}\n'
            append_file(order_summary, message_orders_downloaded)
            logger.info(f"downloading...{order}")
        logger.info(f'number of orders downloaded: {len(orders)}')

        return
    else:
        no_order_table = f'no order table \n ' \
                         f'{number}_2020\n'
        append_file(order_summary, no_order_table)

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

pune_summary = directories_files.district_summary(main_Directory, "pune")
message_complex_number = f':number of complex: {len(this_name_complex_list)}:\n'
append_file(pune_summary, message_complex_number)
for index, value in enumerate(this_name_complex_list):
    message_name_complex = f':{index}  :  {value}\n'
    append_file(pune_summary, message_name_complex)
catch_errors = directories_files.errors_file(main_Directory, 'pune')
# 2.4.c loop over all complexes
start_number = sys.argv[6] if len(sys.argv) >= 7 else "0"
i = int(start_number)
while i < len(this_name_complex_list):
    try:
        # 2.4.1.1 select court complex
        this_name_complex = single_court_complex(i,
                                                 this_value_complex_list,
                                                 this_name_complex_list)
        # 2.4.1.2 select act.
        # If the acts are not available go to the next court complex
        # or if option for particular act is not present go to next court complex
        logger.info(f"{this_name_complex_list[i]}")
        if not select_act():
            logger.info(f'no act found {this_name_complex_list[i]}')
            act_message = f':{this_name_complex_list[i]}' \
                          f':Act Does Not Apply:\n'
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

        # definding dictionary
        base_dictionary = {'Case Type': "BLANK", 'Filing Number': "BLANK",
                           'Filing Date': "BLANK", 'Registration Number': "BLANK",
                           'Registration Date': "BLANK", 'CNR Number': "BLANK",
                           'First Hearing Date': "BLANK", 'Decision Date': "BLANK",
                           'Case Status': "BLANK", 'Nature of Disposal': "BLANK",
                           'Court Number and Judge': "BLANK", ipc: "BLANK",
                           poa: "BLANK", pcso: "BLANK", pcr: "BLANK", cpr: "BLANK",
                           'Other': "BLANK", 'Police Station': "BLANK",
                           'FIR Number': "BLANK", 'Year': "BLANK", 'Petitioner & Adv.': "BLANK",
                           'Respondent & Adv.': "BLANK"}
        fields = base_dictionary.keys()
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
        # create file with headers for writing detials of case.
        case_details_file = directories_files.complex_record_details(
            complex_directory, this_name_complex)
        open_dictionary_with_headers(case_details_file, headers=fields)
        # file with headers for taking details of only PoA cases
        poa_case_details_file = directories_files.complex_records_poa(
            complex_directory, this_name_complex)
        open_dictionary_with_headers(poa_case_details_file, fields)
        view(this_name_complex)
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
                    f'sleeping for 20 secs')
        time.sleep(20)
        continue

logger.info(f'all court complexes in pune completed')
driver.close()
