from cgitb import text
import time
# from tkinter import W
from selenium import webdriver
from pprint import pprint

url = "https://graymirror.substack.com/"

options = webdriver.ChromeOptions();
# options.add_argument('--headless');
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
driver.get(
    driver.find_element_by_class_name("portable-archive-all").get_attribute('href')
)
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    recent_height = driver.execute_script("return document.body.scrollHeight")
    print(f"scrolling screen down. last:{last_height}, " 
          f"now:{recent_height}")
    if recent_height  == last_height:
        break
    time.sleep(2)
    last_height = recent_height

time.sleep(15)

posts = driver.find_elements_by_class_name("post-preview")
table = []
for post in posts:
    p = post.find_element_by_class_name("post-preview-title").get_attribute('href')
    # d = post.find_element_by_class_name("post-date").get_attribute('title')
    table.append((p, ))
pprint(table)
driver.save_screenshot('screen3.png')

for post in table[0:2] + table[-1: -3]:
    parse_post(post[0], driver)

driver.quit()

def parse_post(url, driver){
    driver.get(url)
    post = driver.find_element_by_class_name("single-post")
    title = post.find_element_by_class_name("post-title").text
    subtitle = post.find_element_by_class_name("subtitle").text
    datetime = post.find_element_by_class_name("post-date").get_attribute('title')
    like_count = post.find_element_by_class_name("like-count").text
    body = post.find_element_by_class_name("available-content")
}