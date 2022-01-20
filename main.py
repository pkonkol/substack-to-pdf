import time
# from tkinter import W
from selenium import webdriver
from pprint import pprint

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
posts = driver.find_elements_by_class_name("post-preview")
table = []
for post in posts:
    p = post.find_element_by_class_name("post-preview-title").get_attribute('href')
    # d = post.find_element_by_class_name("post-date").get_attribute('title')
    table.append((p, ))
pprint(table)
driver.quit()
