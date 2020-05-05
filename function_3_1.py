'''
#selecting the act by Value, as CSS selector dosen't match for Nandurbar Dist. Hopefully this works.
But I trial needs to be conducted.

District court website - select state - select district - services - case status - act - back
'''
import datetime
import cv2
import base64
from PIL import Image
from io import BytesIO
import time
import selenium
import self as self
from pytesseract import pytesseract
from selenium.webdriver.common.keys import Keys
import os
from selenium.webdriver.support import expected_conditions as EC, expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    WebDriverException, ElementNotInteractableException

driver = selenium.webdriver.Firefox()
url = r'https://districts.ecourts.gov.in/'
driver.get(url)
# some definatons to be used latter in the code.

invalidCaptcha = "Invalid Captcha"
recordNotFound = "Record Not Found"
wait = WebDriverWait(driver, 180)
waitMid = WebDriverWait(driver, 20)
waitShort = WebDriverWait(driver, 5)


# functions

def district():
    global dateToday

    def complex_and_act():

        def captchcrack():
            def imgtotxt():
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
                area.save('/home/sangharshmanuski/Documents/e_courts/captcha/file_trial.png', 'PNG')
                fullPath = r'/home/sangharshmanuski/Documents/e_courts/captcha'
                f = os.listdir(fullPath)
                desPath = r"/home/sangharshmanuski/Documents/e_courts/editC"
                img = cv2.imread(os.path.join(fullPath, 'file_trial.png'), 0)
                ret, thresh1 = cv2.threshold(img, 111, 255, cv2.THRESH_BINARY)
                cv2.imwrite('/home/sangharshmanuski/Documents/e_courts/editC/oneDisNoLoop.png', thresh1)
                # know the text with pytesseract
                captchaText = pytesseract.image_to_string(
                    Image.open('/home/sangharshmanuski/Documents/e_courts/editC/oneDisNoLoop.png'))
                captcha = driver.find_element_by_id('captcha')
                captcha.send_keys(captchaText)
                driver.find_element_by_css_selector('input.button:nth-child(1)').click()
                time.sleep(3)

            def accept():

                while True:
                    try:
                        driver.switch_to.alert.accept()
                        driver.switch_to.window(driver.current_window_handle[-1])
                        driver.find_element_by_css_selector(
                            '#captcha_container_2 > div:nth-child('
                            '1) > div:nth-child(1) > span:nth-child(3) > a:nth-child(7) > img:nth-child(1)').click()
                        print('alert was present')
                        imgtotxt()
                    except:
                        print('no alret')
                        return

            imgtotxt()
            accept()

        def incorrectcaptcha():
            while True:
                waitmsg = 0
                if driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').is_displayed():
                    incorrect = driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').text
                    if incorrect == invalidCaptcha:
                        print('invalid captcha')
                        captchcrack()
                    else:
                        return print('captcha cracked correctly')
                else:
                    return


        def record():
            if driver.find_element_by_css_selector(
                    'a.someclass').is_displayed():
                listAllView = driver.find_elements_by_css_selector('a.someclass')
                print('downloading the record ' + nameCourtComp)
                # make new dirctory by name of Court Complex
                distDir2 = os.path.join(
                    '/home/sangharshmanuski/Documents/e_courts/mha/downloads3',
                    newDistNameDict, nameCourtComp)
                if not os.path.exists(distDir2):
                    os.makedirs(distDir2)
                x = 0
                for view in listAllView:
                    try:
                        view.click()
                        wait.until(EC.presence_of_element_located((By.ID, 'back_top')))
                        openFile = open(
                            os.path.join(distDir2, "file_" + str(x) + ".html"), "w")
                        openFile.write(driver.page_source)
                        openFile.close()
                        back = driver.find_element_by_id('back_top')
                        back.click()
                        x += 1
                    except (TimeoutException, ElementNotInteractableException):
                        wait.until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR,
                                '#captcha_container_2 > div:nth-child(1) > div:nth-child('
                                '1) > span:nth-child(3) > a:nth-child(7) > img:nth-child(1)')))
                        driver.find_element_by_css_selector('input.button:nth-child(2)').click()
                        driver.close()
                        return print(
                            'While Downloading record for '
                            + nameCourtComp + ' error occured, retrying now...')
                else:
                    time.sleep(2)
                    driver.find_element_by_css_selector('input.button:nth-child(2)').click()


        courtComp = 1
        courtComplexDownload = Select(driver.find_element_by_css_selector('#court_complex_code'))
        courtComplexDownloadList = courtComplexDownload.options
        courtComplexLen = len(courtComplexDownloadList) - 1
        while courtComp < courtComplexLen:
            nameCourtComp = courtComplexDownloadList[courtComp].text
            courtComplexDownload.select_by_index(courtComp)
            acts = Select(driver.find_element_by_css_selector('#actcode'))
            actsOpt = acts.options
            act = 0
            while act < 20:
                if len(actsOpt) < 1:
                    time.sleep(1)
                    act += 1
                else:
                    acts.select_by_value('33')
                    break
            else:
                print('no PoA')
                return
            captchcrack()
            incorrectcaptcha()
               
            if driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').is_displayed():
                courtComp += 1
                continue
            else:
                record()
                courtComp += 1
                continue

    districtListDropdown = Select(driver.find_element_by_css_selector("#sateist"))
    distOptions = districtListDropdown.options
    lenOpts = len(distOptions) - int(1)
    i = 25
    while i <= lenOpts:

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#sateist')))
            # change the name latter. set it to format as per name of the state.
            newDistDropDown = Select(driver.find_element_by_css_selector("#sateist"))
            newDistOptions = newDistDropDown.options
            dateToday = datetime.datetime.now()
            newDistName = newDistOptions[i].text
            newDistNameDict = newDistName + '_' + str(dateToday.day) + '_' + str(dateToday.month) + '_' + str(
                dateToday.year)
            newDistDropDown.select_by_index(i)
            distDir = os.path.join('/home/sangharshmanuski/Documents/e_courts/mha/downloads3', newDistNameDict)
            if not os.path.exists(distDir):
                os.mkdir(distDir)
            # wait for new District Court page to upload fully.
            headingDist = driver.find_element_by_css_selector('.heading')
            if headingDist.text.lower() == newDistName.lower():
                wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.accordion2:nth-child(2)'))).click()
                current = driver.window_handles[0]
                wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR,
                     'div.panel:nth-child(3) > ul:nth-child(1) > li:nth-child(6) > a:nth-child(1)'))).click()
                # wait until new tab opens.
                wait.until(EC.number_of_windows_to_be(2))
                # define new tab by differentiating from current tab.
                newWindow = [window for window in driver.window_handles if window != current][0]
                # switch to the new tab. ref: https://stackoverflow.com/questions/41571217/python-3-5-selenium-how-to-handle-a-new-window-and-wait-until-it-is-fully-lo
                driver.switch_to.window(newWindow)
                # wait till court complex list appears.
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#court_complex_code')))
                # create list of all court complex.
                # 2 approaches - 1 select 2 click.
                time.sleep(5)
                complex_and_act()
                driver.close()
                print("all court complexes in " + newDistName + " completed")
                driver.switch_to.window(current)
                driver.back()

            else:
                time.sleep(5)
                continue
            i += 1

    else:
        return print("all districts completed")


wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sateist > option:nth-child(22)")))
select = Select(driver.find_element_by_css_selector('#sateist'))
options = select.options
select.select_by_visible_text('Maharashtra')
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.region')))
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#sateist')))

district()
