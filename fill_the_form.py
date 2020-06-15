from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class FormFilling:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def court_complex_list(self):
        this = self.driver.current_window_handle
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#court_complex_code')))
        complex_combo = Select(self.driver.find_element_by_css_selector('#court_complex_code'))
        # return list of non-empty values from combo box
        court_complex_names = [o.get_attribute("text")
                               for o in complex_combo.options if o.get_attribute("value") != '']
        court_complex_values = [o.get_attribute("value")
                                for o in complex_combo.options if o.get_attribute("value") != '']
        return court_complex_names, court_complex_values

    def single_court_complex(self, complex=0):
        "returns sigle court complex name and value of the same"
        value_complex = get_districts()[0][complex]
        name_complex = get_districts()[1][complex]
        print(name_complex, value_complex)
        return name_complex, value_complex

    def acts_list(name_complex):
        """Populates list of acts.
        if the list is empty it waits for a 1 sec and tries agin
        after trying 10 times it closes the effort and returns"""
        acts = Select(driver.find_element_by_css_selector('#actcode'))
        acts_list = acts.options
        act = 0
        while len(acts_list) < 2:
            if act < 10:
                time.sleep(1)
                act += 1
            else:
                # if there is no list to populate break out of this function
                return print(f"sorry no act in {name_complex}, go to nex")
        else:
            acts_value = [o.get_attribute("value") for o in acts_list if o.get_attribute("value") != '0']
            acts_name = [o.get_attribute("text") for o in acts_list if o.get_attribute("value") != '0']
        return acts_name, acts_value

    def single_act(actvalue=33):
        "returns sigle court complex name and value of the same"
        act_name = get_districts()[0][actvalue]
        act_value = get_districts()[1][actvalue]
        print(act_name, act_value)
        return act_name, act_value

    def grab_and_crop_captcha():
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
        return area

    def crack_captcha(area):
        "crack captcha with pytsseract and process image before that with cv2"
        "returns text value"
        img = cv2.imread(area, 0)
        ret, thresh1 = cv2.threshold(img, 111, 255, cv2.THRESH_BINARY)
        cv2.imwrite(
            '/home/sangharshmanuski/Documents/e_courts/editC/oneDisNoLoop.png', thresh1)
        # know the text with pytesseract
        captchaText = pytesseract.image_to_string(
            Image.open(
                '/home/sangharshmanuski/Documents/e_courts/editC/oneDisNoLoop.png'))
        return captchaText

    def enter_captcha(captcha_text):
        "enters captcha text taken from crack_catcha(..) function"
        captcha = driver.find_element_by_id('captcha')
        captcha.send_keys(captcha_text)
        driver.find_element_by_css_selector('input.button:nth-child(1)').click()
        time.sleep(1)

    def accept_alert():
        driver.switch_to.alert.accept()

    def wait_msg():
        please_wait = driver.find_element_by_css_selector('#waitmsg')
        if please_wait.is_displayed():
            return True
        else:
            return False

    def wait_msg_wait():
        sleep = 1
        while wait_msg():
            if sleep < 6:
                time.sleep(sleep)
                sleep += 1
                continue
            else:
                break
        return print('result of captch crack ready')


class ErrorSpan():
    """if the error span is displayed after entering captcha, it looks for two options"""

    def __init__(self, incorrect):
        self.incorrect = incorrect

    def invalid_catcha(self):
        """if catcha is invalid it returns true.
        first, if there is wait msg it waits for 5 sec
        waiting only for 5 sec is essential as in case of alert, the wait msg keeps displaying
        even if the alert is accepted"""
        inValidCaptcha = "Invalid Captcha"
        try:
            if self.incorrect == inValidCaptcha:
                print(f'{self.incorrect}, try again')
                return True
            else:
                print('captched cracked correctly')
                return False
        except NoSuchElementException:
            print('captcha cracked')
            return False

    def noRecordFound(self):
        "checcks if no record found message is displayed"
        no_record_found = "Record Not Found"
        try:
            if self.incorrect == no_record_found:
                print(f'{self.incorrect}, please go to next court complex')
                return True
            else:
                print('it is not about availablitly of record')
                return False
        except NoSuchElementException:
            print('captcha cracked')
            return False


def download(name_dist, name_complex):
    newDir = court_complex_dir(name_dist, name_complex)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.someclass')))
    listAllView = driver.find_elements_by_css_selector(
        'a.someclass')
    x = 0
    for view in listAllView:
        try:
            view.click()
            wait.until(EC.presence_of_element_located((By.ID, 'back_top')))
            openFile = open(
                os.path.join(newDir, "file_" + str(x) + ".html"), "w")
            openFile.write(driver.page_source)
            openFile.close()
            back = driver.find_element_by_id('back_top')
            back.click()
            x += 1
        except NoSuchElementException:
            raise
