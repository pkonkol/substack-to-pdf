import time
# from tkinter import W
from selenium import webdriver

url = "https://graymirror.substack.com/"

options = webdriver.ChromeOptions();
options.add_argument('--headless');
options.add_argument('window-size=1920x1080');
driver = webdriver.Chrome(options=options)
resp = driver.get(url)
driver.save_screenshot('screen.png')
driver.find_element_by_xpath('//button[text()="Let me read it first"]').click()
time.sleep(2)
driver.save_screenshot('screen2.png')
driver.quit()