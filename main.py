from cgitb import text
import time
# from tkinter import W
from selenium import webdriver
from selenium.webdriver.common.by import By
from pprint import pprint

url = "https://graymirror.substack.com/"

options = webdriver.ChromeOptions();
# options.add_argument('--headless');
options.add_argument('window-size=1920x1080');
driver = webdriver.Chrome(options=options)

def parse_archive():
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
        time.sleep(0.5)
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

def parse_post(url):
    driver.get(url)
    post = driver.find_element(By.CLASS_NAME, "single-post")
    title = post.find_element(By.CLASS_NAME, "post-title").text
    subtitle = post.find_element(By.CLASS_NAME, "subtitle").text
    datetime = post.find_element(By.CLASS_NAME, "post-date").get_attribute('title')
    like_count = post.find_element(By.CLASS_NAME, "like-count").text
    body = post.find_element(By.CLASS_NAME, "available-content").find_element(By.CLASS_NAME, "body")
    print([e.tag_name for e in  body.find_elements(By.XPATH, '*')]) #'.//*[not(contains(@class, "subscribe-widget"))]')])
    breakpoint()
    pprint((post, title, subtitle, datetime, like_count, body))

# for post in table[0:2] + table[-1: -3]:
#     parse_post(post[0], driver)


if __name__ == "__main__":
    # posts = parse_archive(url)
    # (parse_post(url) for post[0] in posts)
    post_url =  "https://graymirror.substack.com/p/1-a-general-theory-of-collaboration"
    parse_post(post_url)
    driver.quit()