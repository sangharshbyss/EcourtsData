import glob
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
    WebDriverException, ElementNotInteractableException, UnexpectedAlertPresentException

main_Directory = r'/home/sangharshmanuski/Documents/e_courts/mha/downloads4'
log_Directory = r'/home/sangharshmanuski/Documents/e_courts/mha/log'
driver = selenium.webdriver.Firefox()
url = r'https://districts.ecourts.gov.in/'
driver.get(url)
# create wait time variable for regular, short and mid
wait = WebDriverWait(driver, 180)
waitShort = WebDriverWait(driver, 3)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sateist > option:nth-child(22)")))
select = Select(driver.find_element_by_css_selector('#sateist'))
options = select.options
select.select_by_visible_text('Maharashtra')
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.region')))
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#sateist')))
districtListDropdown = Select(driver.find_element_by_css_selector("#sateist"))
distOptions = districtListDropdown.options

# iterate over each district
i = 1
while i < len(distOptions):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#sateist')))
    newDistDropDown = Select(driver.find_element_by_css_selector("#sateist"))
    newDistOptions = newDistDropDown.options
    distName = newDistOptions[i].text
    print(distName)
    newDistDropDown.select_by_index(i)
    # for creating directory as per each district.
    district_directory = os.path.join(
        main_Directory, distName)  # create new
    if not os.path.exists(district_directory):  # if not directory exists, create one
        os.mkdir(district_directory)
    district_log_directory = os.path.join(log_Directory, distName)
    if not os.path.exists(district_log_directory):  # if not directory exists, create one
        os.mkdir(district_log_directory)
    headingDist = driver.find_element_by_css_selector('.heading')
    if headingDist.text.lower() == distName.lower():
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
        time.sleep(3)


        def complex_and_act():
            this = driver.current_window_handle

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
                time.sleep(1)

            def proceed():
                while True:
                    try:
                        waitShort.until(EC.alert_is_present())
                        driver.switch_to.alert.accept()
                        driver.switch_to.window(this)
                        driver.find_element_by_css_selector(
                            '#captcha_container_2 > div:nth-child('
                            '1) > div:nth-child(1) > span:nth-child(3) > a:nth-child(7) > img:nth-child(1)').click()
                        log_file = open(os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                        log_file.write('alert was present' + '\n')
                        print('alert was present')
                        imgtotxt()
                    except:
                        # if the waitmsg is on, wait for 5 sec
                        log_file = open(os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                        log_file.write('no alert' + '\n')
                        print('no alert')
                        waitmsg = 0
                        while driver.find_element_by_css_selector('#waitmsg').is_displayed():
                            if waitmsg < 7:
                                log_file = open(
                                    os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                                log_file.write('wait' + '\n')
                                print('waitmsg')
                                time.sleep(1)
                                waitmsg += 1
                            else:
                                log_file = open(os.path.join(
                                    log_Directory, nameCourtComp + '.txt'), 'a')
                                log_file.write('waiting finished' + '\n')
                                print('waiting finished')
                                break
                        invalidCaptcha = "Invalid Captcha"
                        norecord = "Record Not Found"
                        try:
                            waitShort.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '#errSpan > p:nth-child(1)')))
                            incorrect = driver.find_element_by_css_selector('#errSpan > p:nth-child(1)').text
                            if incorrect == invalidCaptcha:
                                log_file = open(
                                    os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                                log_file.write('Invalid Captcha' + '\n')
                                print('invalid captcha')
                                imgtotxt()
                                continue
                            else:
                                log_file = open(
                                    os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                                log_file.write('Record not Found' + '\n')
                                return print('record not found')

                        except:
                            log_file = open(
                                os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                            log_file.write('Record Found' + '\n')
                            print('record fun started')

                            def record():
                                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.someclass')))
                                listAllView = driver.find_elements_by_css_selector(
                                    'a.someclass')
                                # make new dirctory by name of Court Complex
                                distDir2 = os.path.join(
                                    main_Directory, distName, nameCourtComp)
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
                                        log_file = open(
                                            os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                                        log_file.write(
                                            'While Downloading record for '
                                            + nameCourtComp + ' error occured, retrying now...' + '\n')
                                        return print(
                                            'While Downloading record for '
                                            + nameCourtComp + ' error occured, retrying now...')
                                log_file = open(
                                    os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                                log_file.write('record completed, ' + str(x) + ' records found' + '\n')
                                print('record completed, ' + str(x) + ' records found')
                                return

                            record()
                            print('record function finished')
                            return

            courtComp = 1
            courtComplexDownload = Select(
                driver.find_element_by_css_selector('#court_complex_code'))
            courtComplexDownloadList = courtComplexDownload.options
            courtComplexLen = len(courtComplexDownloadList)
            while courtComp < courtComplexLen:
                nameCourtComp = courtComplexDownloadList[courtComp].text
                log_file = open(os.path.join(log_Directory, nameCourtComp + '.txt'), 'w')
                log_file.write(nameCourtComp + '\n' + '\n')
                print(nameCourtComp)
                courtComplexDownload.select_by_index(courtComp)
                acts = Select(driver.find_element_by_css_selector('#actcode'))
                actsOpt = acts.options
                act = 0
                while len(actsOpt) < 1:
                    if act < 20:
                        time.sleep(1)
                        act += 1
                    else:
                        log_file = open(
                            os.path.join(log_Directory, nameCourtComp + '.txt'), 'a')
                        log_file.write('No PoA' + '\n')
                        print('no PoA')
                        courtComp += 1
                        break
                else:
                    acts.select_by_value('33')

                imgtotxt()
                proceed()
                courtComp += 1


        complex_and_act()
        driver.close()
        print("all court complexes in " + distName + " completed")
        driver.switch_to.window(current)
        driver.back()

    else:
        time.sleep(5)
        continue
    i += 1

wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sateist > option:nth-child(22)")))
select = Select(driver.find_element_by_css_selector('#sateist'))
options = select.options
select.select_by_visible_text('Maharashtra')
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.region')))
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#sateist')))
