#%%
import requests
from bs4 import BeautifulSoup
from process_article import *

def parse_page(url):
    # Step 1: Fetch the content of the page
    response = requests.get(url)
    html_content = response.content

    # Step 2: Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Step 3: Find all article elements
    articles = soup.find_all('article', class_='archive-list')

    # Step 4: Parse each article and extract information
    for article in articles:
        process_article(article)
    # Step 5: Check for "next page" link and recursively call parse_page
    next_page = soup.find('a', class_='next page-numbers')
    if next_page:
        next_url = next_page['href']
        print(f"Moving to next page: {next_url}")
        parse_page(next_url)  # Recursive call to parse the next page


#%%
# Step 1: Fetch the HTML content of the page
url = "https://av-wiki.net/av-actress"
parse_page(url=url)


