# note change courtPuneDistrict variable
# view the page and download it to directory/file. Change file name for every new court at the end of this code.
# only upto entering captcha.
# source https://thereluctanttester.com/2018/01/09/python-selenium-webdriver-working-with-dropdown-options-inside-a-select-tag/
# source https://chercher.tech/python/dropdown-selenium-python
# this code works. type the captch. press enter and boom.... you will get the list.
import os
import time
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import os
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

driver = selenium.webdriver.Firefox()
url = r'https://services.ecourts.gov.in/ecourtindia_v4_bilingual/cases/s_actwise.php?state=D&state_cd=1&dist_cd=19'
driver.get(url)
court = Select(driver.find_element_by_id('court_complex_code'))
courtPuneDistrict = court.select_by_visible_text('Aurangabad, District and Sessions')
actType = Select(driver.find_element_by_id('actcode'))
PoAactType = actType.select_by_visible_text('Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act')
# enter captccha manually with send_keys() method and input()
captcha = driver.find_element_by_id('captcha')
type = input('enter captcha: ')
captcha.send_keys(type)
# submit the form
submit_button = driver.find_element_by_name('submit1')
submit_button.click()

# find text 'view', click on it find back button click and find next view  - for loop
WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.someclass')))
listAllView = driver.find_elements_by_css_selector('a.someclass')
# write data - save the new pages
for i in listAllView:
    i.click()
    openFile = open("/home/sangharshmanuski/Documents/e_courts/aurangabad/rawDownloadedFiles/file_" + str(i) + ".html", "w")
    openFile.write(driver.page_source)
    openFile.close()
    WebDriverWait(driver, 600000).until(EC.presence_of_element_located((By.ID, 'back_top')))
    back = driver.find_element_by_id('back_top')
    back.click()
    WebDriverWait(driver, 50000).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.someclass')))
driver.close()

