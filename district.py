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