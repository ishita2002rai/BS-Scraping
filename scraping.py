import os
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from collections import Counter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

# Base URL of El País
BASE_URL = "https://elpais.com/"

# BrowserStack credentials
BROWSERSTACK_USERNAME = "ishitarai_2kHaBu"
BROWSERSTACK_ACCESS_KEY = "ncT7uqTsnSjyEVCq2SJs"

# BrowserStack capabilities for cross-browser testing
capabilities_list = [
    {"browserName": "Chrome", "browserVersion": "latest", "os": "Windows", "osVersion": "10", "build": "El_pais_Test",
     "browserstack.consoleLogs": "errors"},
    {"browserName": "Firefox", "browserVersion": "latest", "os": "Windows", "osVersion": "10", "build": "El_pais_Test",
     "browserstack.consoleLogs": "errors"},
    {"browserName": "Safari", "browserVersion": "latest", "os": "OS X", "osVersion": "Monterey", "build": "El_pais_Test",
     "browserstack.consoleLogs": "errors"},
    {"browserName": "Chrome", "browserVersion": "latest", "device": "Samsung Galaxy S21", "realMobile": "true",
     "build": "El_pais_Test", "browserstack.consoleLogs": "errors"},
    {"browserName": "Safari", "osVersion": "16", "device": "iPhone 14", "realMobile": "true",
     "build": "El_Pais_Test", "browserstack.consoleLogs": "errors"}

]

def fetch_opinion_articles():
    """
    Fetch the first five articles from the Opinion section of El País.
    Returns a list of dictionaries containing title, content, and image URL.
    """
    response = requests.get(BASE_URL + "opinion/")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", limit=5)
    articles_data = []

    for article in articles:
        title_tag = article.find("h2") or article.find("h1")
        content_tag = article.find("p")
        image_tag = article.find("img")
        title = title_tag.text.strip() if title_tag else "No title found"
        content = content_tag.text.strip() if content_tag else "No content found"
        image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else None
        articles_data.append({"title": title, "content": content, "image_url": image_url})

    return articles_data

def save_image(image_url, filename):
    """
    Save an image from a given URL to a local file.
    """
    if not image_url:
        return
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    except Exception as e:
        print(f"Error saving image: {e}")

def translate_headers(articles):
    """
    Translate article titles from Spanish to English using Google Translate API.
    Adds the translated title to each article and returns updated articles and a list of translated titles.
    """
    translator = Translator()
    translated_headers = []
    for article in articles:
        translated_title = translator.translate(article["title"], src="es", dest="en").text
        translated_headers.append(translated_title)
        article["translated_title"] = translated_title
    return articles, translated_headers

def analyze_headers(translated_headers):
    """
    Analyze repeated words across all translated headers.
    Returns a dictionary with words as keys and their occurrence counts as values.
    """
    words = []
    for header in translated_headers:
        words.extend(header.lower().split())
    word_counts = Counter(words)
    return {word: count for word, count in word_counts.items() if count > 2}

def run_test(capabilities):
    """
    Execute cross-browser testing using BrowserStack for a given set of capabilities.
    """
    options = Options()
    for key, value in capabilities.items():
        options.set_capability(key, value)
    options.set_capability("browserstack.user", BROWSERSTACK_USERNAME)
    options.set_capability("browserstack.key", BROWSERSTACK_ACCESS_KEY)

    driver = webdriver.Remote(command_executor="http://hub-cloud.browserstack.com/wd/hub", options=options)

    try:
        driver.get(BASE_URL + "opinion/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article"))
        )
        articles = driver.find_elements(By.CSS_SELECTOR, "article")
        print(f"[{capabilities.get('browserName', capabilities.get('device', 'Desktop'))}] Found {len(articles)} articles.")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Step 1: Fetch articles
    articles = fetch_opinion_articles()

    # Step 2: Save images locally
    os.makedirs("images", exist_ok=True)
    for idx, article in enumerate(articles):
        if article["image_url"]:
            save_image(article["image_url"], f"images/article_{idx + 1}.jpg")

    # Step 3: Translate article headers
    articles, translated_headers = translate_headers(articles)

    # Step 4: Analyze translated headers
    repeated_words = analyze_headers(translated_headers)
    print("\nRepeated Words:", repeated_words)

    # Step 5: Display article titles and content
    print("\nArticles Summary:")
    for idx, article in enumerate(articles, 1):
        print(f"\nArticle {idx}:")
        print(f"Title (Original): {article['title']}")
        print(f"Title (Translated): {article['translated_title']}")
        print(f"Content: {article['content']}")

    # Step 6: Perform cross-browser testing
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(run_test, capabilities_list)
