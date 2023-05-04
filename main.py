import os
import sys
import time
import re
import json
import wget
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint
from ebooklib import epub
from lxml.etree import ParserError

POST_RETRY_LIMIT = 5
FILTER = None #FILTER = "^\s*#" # Must be a vaiil regexp
ALLOW_PAYWALLED = True
PAYWALLED_ONLY = False
EMAIL = os.environ.get("SUBSTACK_EMAIL")
PASSWORD = os.environ.get("SUBSTACK_PASS")
WEB_TIMEOUT = 30
EXCLUSION_STRING = 'self::source or contains(@id,"§") or contains(@class,"subscribe-widget") or contains(@class,"image-link-expand")'

options = webdriver.ChromeOptions();
options.add_argument('--headless');
options.add_argument('log-level=1')
driver = webdriver.Chrome(options=options)

def get_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def parse_archive(url, limit=-1, filter=None):
    driver.get(url + '/archive?sort=new')
    blog_name = driver.find_element(By.XPATH, '//link[@rel="alternate"][@href="/feed"]').get_attribute("title")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        WebDriverWait(driver, WEB_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "post-preview-silhouette"))
        )
        recent_height = driver.execute_script("return document.body.scrollHeight")
        print(f"scrolling screen down. last:{last_height}, " 
              f"now:{recent_height}")
        if recent_height  == last_height:
            break
        last_height = recent_height

    posts = driver.find_elements(By.CLASS_NAME, "post-preview")
    posts_parsed = []
    for post in posts:
        url = post.find_element(By.CLASS_NAME, "post-preview-title").get_attribute('href')
        title = post.find_element(By.CLASS_NAME, "post-preview-title").text
        if filter and not re.match(filter, title):
            continue
        try:
            post.find_element(By.CLASS_NAME, "audience-lock")
            paywalled = True
        except NoSuchElementException:
            paywalled = False
        posts_parsed.append({'url': url, 'paywalled': paywalled, 'title': title})
    pprint(posts_parsed)
    return {'blog_name': blog_name, 'posts': posts_parsed}

def parse_post(url):
    print(f'parsing {url}')
    driver.get(url)

    post = WebDriverWait(driver, WEB_TIMEOUT).until(
        EC.presence_of_element_located((By.CLASS_NAME, "single-post")) # d.find_element(By.CLASS_NAME, "single-post")
    )

    clean_post(post)

    post_json = json.loads(driver.find_element(By.XPATH, '//script[@type="application/ld+json"]').get_attribute('innerHTML'))

    f = "%Y-%m-%dT%H:%M:%S%z"
    out = dt.strptime(post_json["datePublished"], f)
    try:
        driver.find_element(By.XPATH, '//div[@class="single-post"]//div[contains(@class,"paywall")]')
        paywalled = True
    except NoSuchElementException:
        paywalled = False

    title = post.find_element(By.CLASS_NAME, "post-title").text
    try:
        subtitle = post.find_element(By.CLASS_NAME, "subtitle").text
    except NoSuchElementException:
        print('This post has no subtittle')
        subtitle = ""

    datetime = out.strftime("%Y-%m-%d %H:%M:%S")
    try:
        like_count = post.find_element(By.XPATH, '//div[contains(concat(" ",normalize-space(@class)," "),"like-button-container")]//div[@class="label"]').text
    except NoSuchElementException:
        print('Failed to find like count')
        like_count = 0
    body = post.find_element(By.CLASS_NAME, "available-content").find_element(By.CLASS_NAME, "body")
    
    body = post.find_element(By.CLASS_NAME, "available-content").find_element(By.CLASS_NAME, "body")
    hoist_images(body)
    body = post.find_element(By.CLASS_NAME, "available-content").find_element(By.CLASS_NAME, "body")
    images = parse_images(body)
    body = post.find_element(By.CLASS_NAME, "available-content").find_element(By.CLASS_NAME, "body")
    text_html = remove_emojis(body.get_attribute("innerHTML"))
    pprint((post, title, subtitle, datetime, like_count, body))
    print(f'title: {title}, paywalled: {paywalled}, likes: {like_count}')
    return {'title': title, 'subtitle': subtitle, 'date': datetime,
            'like_count': like_count, 'text_html': text_html,
            'paywalled': paywalled,
            'images': images
           }

def clean_post(post):
    f = f'.//*[{EXCLUSION_STRING}]'
    unsupported = post.find_elements(By.XPATH, f)
    for e in unsupported:
        remove_element(e)

def remove_element(el):
    try:
        c_attr = el.get_attribute("class")
        print(f"Removing element {el} with class attr {c_attr}")
        driver.execute_script("var element = arguments[0]; element.parentNode.removeChild(element);", el)
    except Exception as e:
        print(e)

def hoist_element(el):
    try:
        driver.execute_script("var element = arguments[0]; var parent = element.parentNode; var grandparent = parent.parentNode; grandparent.append(element); grandparent.removeChild(parent);", el)
    except Exception as e:
        print(e)

def set_attribute(el, attribute, value):
    try:
        driver.execute_script(f'arguments[0].setAttribute("{attribute}", "{value}")', el)
    except Exception as e:
        print(e)

def remove_attribute(el, attribute):
    try:
        driver.execute_script(f'arguments[0].removeAttribute("{attribute}")', el)
    except Exception as e:
        print(e)

def clean_html(body):
    try:
        f = f'.//*[not({EXCLUSION_STRING})]'
        text_list = [
            e.get_attribute('outerHTML')
            for e 
            in body.find_elements(By.XPATH, f)
        ]
        return "".join(text_list)
    except ParserError as e:
        print(e)
        pass

def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

def sign_in(email, password=None, login_link=None):
    print(f"signing for email: {email}")
    driver.get("https://substack.com/sign-in")
    driver.find_element(By.CLASS_NAME, "substack-login__login-option").click()
    driver.find_element(By.XPATH, '//input[@name="email"]').send_keys(email)
    driver.find_element(By.XPATH, '//input[@name="password"]').send_keys(password)
    driver.find_element(By.CLASS_NAME, "substack-login__go-button").click()
    WebDriverWait(driver, WEB_TIMEOUT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'homepage-nav-user-indicator')) 
    )
    print("signed in")

def hoist_images(body):
    imgs = body.find_elements(By.XPATH, './/a[contains(@class,"image-link")]//picture')
    for i in imgs:
        hoist_element(i.find_element(By.XPATH, "parent::*"))

def parse_images(body):    
    imgs = body.find_elements(By.XPATH, ".//img")
    img_map = []
    for i in imgs:
        img_map.append(fix_image(i))
    return img_map

def fix_image(i):
    src = i.get_attribute("src")
    #Download img from src
    file_name = wget.download(src)
    link = f"images/{file_name}"
    set_attribute(i, "src", link)
    return [file_name, link]



if __name__ == "__main__":
    if EMAIL and PASSWORD:
        sign_in(EMAIL, PASSWORD)
    archive = parse_archive(sys.argv[1], limit=-1, filter=FILTER)

    book = epub.EpubBook()
    book.set_identifier('id00000')
    book.set_title(archive['blog_name'])
    book.set_language('en')
    book.add_metadata('DC', 'description', 'generated by pkonkol/substack-to-pdf')
    book.add_metadata('DC', 'publisher', 'substack-to-pdf')

    print(len(archive['posts']))

    toc = []
    spine = []
    not_posts = []
    for i, post in enumerate(archive['posts'][::-1]):
        j = 0
        while True:
            try:
                if ALLOW_PAYWALLED or post['paywalled'] == PAYWALLED_ONLY:
                    p = parse_post(post['url'])
                break
            except TimeoutException:
                j += 1
                if j >= POST_RETRY_LIMIT:
                    break
                print(f'retrying parsing {post["url"]} for {j} time')
        if not p:
            not_posts.append(post["url"])
            continue

        content = (
            f'<h1>{p["title"]}</h1>'
             '<p>'
            f'<time datetime="{p["date"]}"> {p["date"]} </time>'
            f'<span>Likes:{p["like_count"]} </span><span> Paywalled: {p["paywalled"]}</span>'
             '</p>'
            f'<a href="{post["url"]}">URL: {post["url"]}</a>'
            f'<h2>{p["subtitle"]}</h2>'
            f'{p["text_html"]}'
        )

        chapter = epub.EpubHtml(
            title=p['title'],
            file_name = str(i) + '.' + get_filename(p['title']) + '.xhtml',
            lang='en',
            content= content
        )

        book.add_item(chapter)
        spine.append(chapter)
        toc.append(epub.Link(str(i) + '.' + get_filename(p['title']) + '.xhtml', p['title'], ""))

        for i in p["images"]:
            # load Image file
            with open(i[0], "rb") as image:
                b = bytearray(image.read())
                extension = os.path.splitext(i[0])[1]
                # define Image file path in .epub
                image_item = epub.EpubItem(uid=i[0], file_name=i[1], media_type=f'image/{extension}', content=b)

                # add Image file
                book.add_item(image_item)

            #Cleanup file
            os.remove(i[0])

            

    pprint(f'not posts: {not_posts}')

    book.toc = toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = (['nav',] + spine)
    try:
        epub.write_epub(get_filename(archive['blog_name']) + '.epub', book, {})
    except ParserError as e:
        print(e)
    finally:
        driver.quit()