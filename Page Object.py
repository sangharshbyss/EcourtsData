import base64
from typing import List
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import os
from PIL import Image
from io import BytesIO
import cv2
from pytesseract import pytesseract
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

# constants
url = r'https://districts.ecourts.gov.in/'

options = FirefoxOptions()
# options.add_argument("--headless")
options.add_argument("--private-window")
driver = webdriver.Firefox(options=options)
# base dir path for downloading files:
main_Directory = r'/home/sangharshmanuski/Documents/e_courts/mha/downloads6'
combo_identifier = '#sateist'
wait = WebDriverWait(driver, 180)
waitShort = WebDriverWait(driver, 3)


# FUNCTIONS

def get_states(driver) -> List[str]:
    """Get list of States/UT from combo box
    Return a list of strings
    """
    try:
        # wait for combo box to be ready
        print("Waiting for combo box (States/UT)...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, combo_identifier)))
        print("Combo box should be ready, continue")
    except TimeoutException:
        print("Timed out/failed to load page")

    states_combo = Select(driver.find_element_by_css_selector(combo_identifier))

    # return list of non-empty values from combo box
    state_list = [o.get_attribute("value") for o in states_combo.options if o.get_attribute("value") != '']
    return state_list


def get_districts():
    """
    Get list of districts form options
    It returns two values.
    1 is name (text from the element) of the district
    2 is value (attribute value) of that district
    """
    try:
        # wait for page to open and banner of district court to appear.
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.region')))
    except TimeoutException:
        print("Timed out/failed to load page")

    states_combo = Select(driver.find_element_by_css_selector(combo_identifier))
    # return list of non-empty values from combo box
    districts_names = [o.get_attribute("text") for o in states_combo.options if o.get_attribute("value") != '']
    district_values = [o.get_attribute("value") for o in states_combo.options if o.get_attribute("value") != '']
    return districts_names, district_values


def single_district(dist_number, some_districts_names=None, some_districts_values=None):
    "returns singnle district name and value of the district"
    name_dist = some_districts_names[dist_number]
    value_dist = some_districts_values[dist_number]
    district_option = Select(driver.find_element_by_css_selector(combo_identifier))
    district_option.select_by_value(value_dist)
    return name_dist, value_dist


def match_heading(some_district_name=None):
    heading_dist = driver.find_element_by_css_selector('.heading')
    heading_dist_lower = heading_dist.text.lower()
    some_district_name_lower = some_district_name.lower()
    while heading_dist_lower != some_district_name_lower:
        time.sleep(1)
        print(f'not matched {heading_dist.text.lower} and {some_district_name.lower}')
    else:
        return True


def case_status_by_act():
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.accordion2:nth-child(2)'))).click()
    select_case_status_by_act = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR,
         'div.panel:nth-child(3) > ul:nth-child(1) > li:nth-child(6) > a:nth-child(1)')))
    select_case_status_by_act.click()
    return select_case_status_by_act


def court_complex_list():
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#court_complex_code')))
    complex_combo = Select(driver.find_element_by_css_selector('#court_complex_code'))
    # return list of non-empty values from combo box
    court_complex_names = [o.get_attribute("text")
                           for o in complex_combo.options if o.get_attribute("value") != '0']
    court_complex_values = [o.get_attribute("value")
                            for o in complex_combo.options if o.get_attribute("value") != '0']
    print(court_complex_values, court_complex_names)
    return court_complex_names, court_complex_values


def single_court_complex(complex_number, value_complex_list=None, name_complex_list=None):
    # returns single court complex name and value of the same
    complex_combo = Select(driver.find_element_by_css_selector('#court_complex_code'))
    value_complex = value_complex_list[complex_number]
    name_complex = name_complex_list[complex_number]
    complex_combo.select_by_value(value_complex)
    print(name_complex)
    return name_complex


def select_act(some_name_complex=None):
    """Populates list of acts.
    if the list is empty it waits for a 1 sec and tries again
    after trying 10 times it closes the effort and returns"""
    acts = Select(driver.find_element_by_css_selector('#actcode'))
    act_list = acts.options
    second = 0
    while len(act_list) < 2:
        if second < 10:
            time.sleep(1)
            second += 1
        else:
            print(f"sorry no act in {some_name_complex}")
            return False
    else:
        print('got it')
        acts.select_by_value('33')
        return True


def accept_alert(tab=None):
    try:
        waitShort.until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        driver.switch_to.window(tab)
        print('alert accepted')
        return True
    except (NoSuchElementException, TimeoutException):
        print('no alert present')
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
    return print('result of captcha crack ready')


def invalid_captcha():
    # if captcha is invalid it returns true.
    try:
        incorrect = driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').text
        in_valid_captcha = "Invalid Captcha"
        if incorrect == in_valid_captcha:
            print(f'{incorrect}, try again')
            return True
        else:
            print('captcha cracked correctly')
            return False
    except NoSuchElementException:
        print('captcha cracked')
        return False


def captcha_to_text():
    "captures the captcha image"
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
    full_path = r'/home/sangharshmanuski/Documents/e_courts/captcha'
    area.save(os.path.join(full_path, 'file_trial.png'), 'PNG')
    img = cv2.imread(os.path.join(full_path, 'file_trial.png'), 0)
    ret, thresh1 = cv2.threshold(img, 111, 255, cv2.THRESH_BINARY)
    cv2.imwrite(
        '/home/sangharshmanuski/Documents/e_courts/editC/oneDisNoLoop.png', thresh1)
    # know the text with pytesseract
    captcha_text = pytesseract.image_to_string(
        Image.open(
            '/home/sangharshmanuski/Documents/e_courts/editC/oneDisNoLoop.png'))
    return captcha_text


def submit_form():
    # "enters captcha text taken from crack_captcha(..) function"
    captcha = driver.find_element_by_id('captcha')
    captcha.send_keys(captcha_to_text())
    driver.find_element_by_css_selector('input.button:nth-child(1)').click()
    time.sleep(1)


def no_record_found(courtcomplex=None):
    # checks if no record found message is displayed

    try:
        no_record = driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').text
        no_record_available = "Record Not Found"
        if no_record == no_record_available:
            print(f'no record @ {courtcomplex} please go to next court complex')
            return True
        else:
            print('tell me what else is it?')
            return False
    except NoSuchElementException:
        print('captcha cracked, record available, download')
        return False



def download(some_district=None, some_complex=None):
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.someclass')))
    list_all_view = driver.find_elements_by_css_selector(
        'a.someclass')
    record = 0
    for view in list_all_view:
        print('downloading')
        try:
            view.click()
            wait.until(EC.presence_of_element_located((By.ID, 'back_top')))
            open_file = open(
                os.path.join(main_Directory, some_district, some_complex, "file_" + str(record) + ".html"), "w")
            open_file.write(driver.page_source)
            open_file.close()
            back = driver.find_element_by_id('back_top')
            back.click()
            record += 1
        except NoSuchElementException:
            raise
    print(f'{this_name_complex} downloaded')



def dist_dir(some_district_name=None):
    district_directory = os.path.join(
        main_Directory, some_district_name)  # create new
    if not os.path.exists(district_directory):  # if not directory exists, create one
        os.mkdir(district_directory)
    return district_directory


def court_complex_dir(district_directory=None, name_complex=None):
    # makes separate directory particular court complex
    court_complex_directory = os.path.join(
        main_Directory, district_directory, name_complex)  # create new
    if not os.path.exists(court_complex_directory):  # if not directory exists, create one
        os.mkdir(court_complex_directory)
    return court_complex_directory


# MAIN CODE

# load the main page
driver.get(url)

# Step 1 - select a state from list of states
# fixed selection from list. As only Maharashtra is covered now.

state_option = Select(driver.find_element_by_css_selector(combo_identifier))
state = state_option.select_by_value('maharashtra')
list_districts_names, list_districts_values = get_districts()
# Step 2 - district object created
for x in list_districts_names:
    print(f'iteration: {list_districts_names.index(x)}')
    # step 2.1- select single district
    this_district, this_value = single_district(list_districts_names.index(x),
                                                list_districts_names,
                                                list_districts_values)
    print(f'{this_district} is selected')
    # step 2.2 - create directory by district name, if not existing
    dist_dir(this_district)
    # step 2.3 - check if page has fully loaded otherwise wait
    match_heading(this_district)
    # step 2.3.a create variable for window handle
    current = driver.window_handles[0]
    # step 2.4 - a. select case status by act and b. switch to new window
    case_status_by_act()
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
    print(enumerate(this_name_complex_list))
    # 2.4.c loop over all complexes
    '''
    for i in this_name_complex_list:

        # 2.4.1.1 select court complex
        this_name_complex = single_court_complex(this_name_complex_list.index(i),
                                                 this_value_complex_list,
                                                 this_name_complex_list)
        # 2.4.1.2 select act. 
        # If the acts are not available go to the next court complex
        # or if option for particular act is not present go to next court complex
        if not select_act(this_name_complex):
            print('act not found, retrying...')
            driver.find_element_by_css_selector('input.button:nth-child(2)').click()
            single_court_complex(this_name_complex_list.index(i),
                                 this_value_complex_list,
                                 this_name_complex_list)
            if not select_act(this_name_complex):
                continue
        while True:
            submit_form()
            print('captcha entered')
            if accept_alert(newWindow):
                print('... again captcha')
                driver.find_element_by_css_selector('#captcha_container_2 '
                                                    '> div:nth-child(1) > div:nth-child(1) '
                                                    '> span:nth-child(3) > a:nth-child(7) '
                                                    '> img:nth-child(1)').click()
                time.sleep(1)
                print('refresh captcha')
                continue
            else:
                print('go on')
            if not invalid_captcha():
                print('captcha cracked going out of the loop')
                break
            else:
                print('incorrect')
                continue
        # 2.4.5 if no record found go the next court complex
        if no_record_found(this_name_complex):
            continue  # skip rest of the code and continue the for loop from start.
        else:
            # 2.4.6 make new directory
            court_complex_dir(this_district, this_name_complex)
            # 2.4.7 download all the records
            try:
                download(this_district, this_name_complex)
            except (ElementNotInteractableException, TimeoutException):
                driver.refresh()
                print(f'exception was present. Recheck {this_name_complex} again.')
                print(f'skipping {this_name_complex} for now')
             continue
    '''
    print(f'all court complexes in {this_district} completed')
    driver.close()


    # 2.4.8 close the form page
driver.close()

# 2.5 all districts completed print statement and go to state-option page.
print(f"all districts in {state} completed")
driver.back()
