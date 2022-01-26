import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pprint import pprint
from ebooklib import epub


options = webdriver.ChromeOptions();
options.add_argument('--headless');
options.add_argument('window-size=1920x1080');
options.add_argument('log-level=1')
driver = webdriver.Chrome(options=options)

def parse_archive(url, limit=-1):
    driver.get(url)
    driver.find_element(By.XPATH, '//button[text()="Let me read it first"]').click()
    time.sleep(1)
    posts = driver.find_elements(By.CLASS_NAME, "post-preview")
    table = []
    driver.get(
        driver.find_element(By.CLASS_NAME, "portable-archive-all").get_attribute('href')
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

    time.sleep(16)

    posts = driver.find_elements_by_class_name("post-preview")
    table = []
    for post in posts[0:limit]:
        url = post.find_element(By.CLASS_NAME, "post-preview-title").get_attribute('href')
        # d = post.find_element_by_class_name("post-date").get_attribute('title')
        table.append({'url': url,})
    pprint(table)
    return table

def parse_post(url):
    print(f'parsing {url}')
    driver.get(url)
    driver.implicitly_wait(20)
    time.sleep(1)
    try:
        post = driver.find_element(By.CLASS_NAME, "single-post")
    except NoSuchElementException:
        print('Not a post ')
        return {'title': "", 'subtitle': "", 'date': "", 'likes': "", 'text_html': ""}
    title = post.find_element(By.CLASS_NAME, "post-title").text
    try:
        subtitle = post.find_element(By.CLASS_NAME, "subtitle").text
    except NoSuchElementException:
        print('This post has no subtittle')
        subtitle = ""

    datetime = post.find_element(By.CLASS_NAME, "post-date").get_attribute('title')
    like_count = post.find_element(By.CLASS_NAME, "like-count").text
    body = post.find_element(By.CLASS_NAME, "available-content").find_element(By.CLASS_NAME, "body")
    text_list = [e.get_attribute('outerHTML') for e in  body.find_elements(By.XPATH, './*[not(contains(@class,"subscribe-widget"))]')]
    text_html = '\n'.join(text_list)
    # breakpoint(
    # pprint((post, title, subtitle, datetime, like_count, body))
    driver.implicitly_wait(0)
    return {'title': title, 'subtitle': subtitle, 'date': datetime, 'likes': like_count, 'text_html': text_html }
    # f = open('test.txt', 'w') #f"donwload/{url}.txt")
    # f.write(text_html)
    # f.close()


if __name__ == "__main__":
    posts = parse_archive(sys.argv[1], limit=3)

    book = epub.EpubBook()
    book.set_identifier('id00000')
    book.set_title('Substack-to-pdf')
    book.set_language('en')

    toc = []
    for i, post in enumerate(posts):
        p = parse_post(post['url'])
        chapter = epub.EpubHtml(title=p['title'], file_name=f'{i}.xhtml', lang='en')
        chapter.content = p['text_html']
        book.add_item(chapter)
        toc.append(epub.Link(f'{i}.xhtml', p['title'], 'huj123'))

    book.toc = toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ('nav')
    epub.write_epub('test.epub', book, {})

    driver.quit()