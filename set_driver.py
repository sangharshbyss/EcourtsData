from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def chrome_driver():
    # set chrome options for automatic download without popup.
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory":
            r'/home/sangharshmanuski/Documents/ecourts_bail_disposed/2020/orders',
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver
