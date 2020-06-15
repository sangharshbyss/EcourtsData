"This included classes for Page Ojbect orientated web scrapping"
import base64
from typing import List
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
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
from selenium.common.exceptions import NoSuchElementException

# constants
url = r'https://districts.ecourts.gov.in/'

options = FirefoxOptions()
# options.add_argument("--headless")
options.add_argument("--private-window")
driver = webdriver.Firefox(options=options)
# base dir path for downloading files:
main_Directory = r'/home/sangharshmanuski/Documents/e_courts/mha/downloads5'
combo_identifier = '#sateist'
wait = WebDriverWait(driver, 180)
waitShort = WebDriverWait(driver, 3)


# FUNCTIONS


# 2. create list of districts
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


class District:
    """object = selected district page
    behaviour 1 = check if page has loaded fully
    behaviour 2 = identify "case status by act" and return the identifier.
     behaviour 3 = click on identifier and swich the window. returns newly opened window"""

    def __init__(self, driver, dist, dist_number=0):
        self.driver = driver
        self.dist = dist
        self.dist_number = dist_number

    def single_district(self):
        "returns signle district name and value of the district"
        name_dist = self.dist_number
        value_dist = self.dist_number
        print(name_dist, value_dist)
        district_option = Select(self.driver.find_element_by_css_selector(combo_identifier))
        selected_dist = district_option.select_by_value(value_dist)
        selected_dist.click()
        return name_dist, value_dist

    def dist_dir(self):
        district_directory = os.path.join(
            main_Directory, self.dist)  # create new
        if not os.path.exists(district_directory):  # if not directory exists, create one
            os.mkdir(district_directory)
        return district_directory

    def match_heading(self):
        heading_dist = self.driver.find_element_by_css_selector('.heading')
        while heading_dist.text.lower() != self.dist.lower():
            time.sleep(1)
        else:
            return True

    def case_status_act(self):
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.accordion2:nth-child(2)'))).click()
        select_case_status_by_act = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR,
             'div.panel:nth-child(3) > ul:nth-child(1) > li:nth-child(6) > a:nth-child(1)')))
        return select_case_status_by_act

    def switch_window(self, select_case_status_by_act):
        current = self.driver.window_handles[0]
        select_case_status_by_act.click()
        wait.until(EC.number_of_windows_to_be(2))
        # define new tab by differentiating from current tab.
        new_window = [window for window in driver.window_handles if window != District.single_district(self)[2]][0]
        # switch to the new tab. ref:
        # https://stackoverflow.com/questions/41571217
        # /python-3-5-selenium-how-to-handle-a-new-window-and-wait-until-it-is-fully-lo
        self.driver.switch_to.window(new_window)


class FormFilling(District):
    '''object = newly opend tab from class district method switch window
methods = feel the form 1. court complex 2. act [sub class - 3. captcha crack 4. check if catcha is right]
5. check if records are found 6. download records if available. '''

    def __init__(self, driver, dist, dist_number, complex_number=0):
        self.complex_number = complex_number
        District.__init__(driver, dist, dist_number)

    def court_complex_list(self):
        this = self.driver.current_window_handle
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#court_complex_code')))
        complex_combo = Select(self.driver.find_element_by_css_selector('#court_complex_code'))
        # return list of non-empty values from combo box
        court_complex_names = [o.get_attribute("text")
                               for o in complex_combo.options if o.get_attribute("value") != '']
        court_complex_values = [o.get_attribute("value")
                                for o in complex_combo.options if o.get_attribute("value") != '']
        return court_complex_names, court_complex_values, complex_combo, this

    def single_court_complex(self):
        "returns sigle court complex name and value of the same"
        value_complex = self.court_complex_list()[1].index(self.complex_number)
        name_complex = self.court_complex_list()[0].index(self.complex_number)
        self.court_complex_list()[2].select_by_value(value_complex)
        print(name_complex, value_complex)
        return name_complex, value_complex

    def acts_list(self):
        """Populates list of acts.
        if the list is empty it waits for a 1 sec and tries agin
        after trying 10 times it closes the effort and returns"""
        name_of_court_complex = self.single_court_complex()[0]
        acts = Select(self.driver.find_element_by_css_selector('#actcode'))
        acts_list = acts.options
        second = 0
        while len(acts_list) < 2:
            if second < 10:
                time.sleep(1)
                second += 1
            else:
                # if there is no list to populate break out of this function
                print(f"sorry no act in {name_of_court_complex}, go to nex")
                return False
        else:
            acts_value = [o.get_attribute("value") for o in acts_list if o.get_attribute("value") != '0']
            acts_name = [o.get_attribute("text") for o in acts_list if o.get_attribute("value") != '0']
        return acts_name, acts_value, acts

    def act_exist(self, act_value=33):
        "returns sigle court complex name and value of the same"
        if self.acts_list():
            try:
                act_name = self.acts_list()[0][act_value]
                act_value = self.acts_list()[1][act_value]
                print(act_name, act_value)
                return True
            except NoSuchElementException:
                return False
        else:
            return False

    def select_act(self, act_value=33):
        self.acts_list()[2].select_by_value(act_value)

    def no_record_found(self):
        "checcks if no record found message is displayed"
        no_record = self.driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').text
        no_record_found = "Record Not Found"
        try:
            if no_record == no_record_found:
                print(f'{no_record}, please go to next court complex')
                return True
            else:
                print('it is not about availablitly of record')
                return False
        except NoSuchElementException:
            print('captcha cracked')
            return False

    def court_complex_dir(self):
        court_complex_directory = os.path.join(
            main_Directory, self.dist, self.single_court_complex()[self.complex_number])  # create new
        if not os.path.exists(court_complex_directory):  # if not directory exists, create one
            os.mkdir(court_complex_directory)
        return court_complex_directory

    def download(self):
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.someclass')))
        listAllView = self.driver.find_elements_by_css_selector(
            'a.someclass')
        x = 0
        for view in listAllView:
            try:
                view.click()
                wait.until(EC.presence_of_element_located((By.ID, 'back_top')))
                openFile = open(
                    os.path.join(self.court_complex_dir(), "file_" + str(x) + ".html"), "w")
                openFile.write(driver.page_source)
                openFile.close()
                back = self.driver.find_element_by_id('back_top')
                back.click()
                x += 1
            except NoSuchElementException:
                raise

    def grab_and_crop_captcha(self):
        "captures the captcha image"
        elem = self.driver.find_element_by_id("captcha_image")
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
        return area

    def img_to_text(self):
        "crack captcha with pytsseract and process image before that with cv2"
        "returns text value"
        img = cv2.imread(self.grab_and_crop_captcha(), 0)
        ret, thresh1 = cv2.threshold(img, 111, 255, cv2.THRESH_BINARY)
        cv2.imwrite(
            '/home/sangharshmanuski/Documents/e_courts/editC/oneDisNoLoop.png', thresh1)
        # know the text with pytesseract
        captchaText = pytesseract.image_to_string(
            Image.open(
                '/home/sangharshmanuski/Documents/e_courts/editC/oneDisNoLoop.png'))
        return captchaText

    def enter_captcha(self):
        "enters captcha text taken from crack_catcha(..) function"
        captcha = self.driver.find_element_by_id('captcha')
        captcha.send_keys(self.img_to_text())
        self.driver.find_element_by_css_selector('input.button:nth-child(1)').click()
        time.sleep(1)

    def accept_alert(self):
        waitShort.until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        self.driver.switch_to.window(self.court_complex_list()[3])

    def wait_msg(self):
        please_wait = self.driver.find_element_by_css_selector('#waitmsg')
        if please_wait.is_displayed():
            return True
        else:
            return False

    def wait_msg_wait(self):
        sleep = 1
        while self.wait_msg():
            if sleep < 6:
                time.sleep(sleep)
                sleep += 1
                continue
            else:
                break
        return print('result of captch crack ready')

    def invalid_captcha(self):
        """if catcha is invalid it returns true.
        first, if there is wait msg it waits for 5 sec
        waiting only for 5 sec is essential as in case of alert, the wait msg keeps displaying
        even if the alert is accepted"""
        incorrect = self.driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').text
        inValidCaptcha = "Invalid Captcha"
        try:
            if incorrect == inValidCaptcha:
                print(f'{incorrect}, try again')
                return True
            else:
                print('captched cracked correctly')
                return False
        except NoSuchElementException:
            print('captcha cracked')
            return False


# MAIN CODE

# load the main page
driver.get(url)

# Step 1 - select a state from list of states
# fixed selection from list. As only Mahrashtra is covered now.

state_option = Select(driver.find_element_by_css_selector(combo_identifier))
state = state_option.select_by_value('maharashtra')

# Step 2 - district object created
for x in get_districts()[0]:
    districtCourt = District(driver=driver,
                             dist=get_districts()[1].index(x),
                             dist_number=get_districts()[0].index(x),
                             )
    # step 2.1- select single district
    districtCourt.single_district()
    # step 2.2 - create directory by district name, if not existing
    districtDirectory = districtCourt.dist_dir()
    # step 2.3 - check if page has fully loaded otherwise wait
    districtCourt.match_heading()
    # step 2.4 - a. select case status by act and b. switch to new window
    districtCourt.switch_window(districtCourt.case_status_act())
    # step2.4.1 -Form filling started
    formPage = FormFilling(districtCourt.driver, districtCourt.dist, districtCourt.dist_number, 0)
    for i in formPage.court_complex_list()[1]:
        # 2.4.1.1 select court complex
        formPage.single_court_complex()
        ''' 2.4.1.2 select act. 
        If the acts are not available go to the next court complex
        or if option for particular act is not present go to next court complex'''
        if not formPage.acts_list():
            continue  # skip reset of the code and start again.
        else:
            if not formPage.act_exist():
                continue # skip reset of the code and go to start of for loop.
            else:
                formPage.select_act()
        # 2.4.1.3 grab and crop captcha. returns cropped image
        formPage.grab_and_crop_captcha()
        # 2.4.1.4 convert image to text return text.
        formPage.img_to_text()
        # 2.4.1.5 enter the captcha and click submit button.
        formPage.enter_captcha()
        # 2.4.2 if alter it present, accept it.
        formPage.accept_alert()
        # 2.4.3 if wait msg is present, wait.
        if formPage.wait_msg():
            formPage.wait_msg_wait()
        # 2.4.4 if captcha is invalid again do captcha crack and try
        while formPage.invalid_captcha():
            formPage.grab_and_crop_captcha()
            formPage.img_to_text()
            formPage.enter_captcha()
            formPage.accept_alert()
            formPage.wait_msg_wait()
        # 2.4.5 if no record found go the next court complex
        if formPage.no_record_found():
            continue # skip rest of the code and continue the for loop from start.
        else:
            # 2.4.6 make new directory
            formPage.court_complex_dir()
            # 2.4.7 download all the records
            formPage.download()
    # 2.4.8 close the form page
    formPage.driver.close()
# 2.5 all districts completed print statement and go to state-option page.
print(f"all districts in {state} completed")
driver.back()
