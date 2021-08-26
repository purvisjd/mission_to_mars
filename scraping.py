#Import Splinter, BeautifulSoup, and Pandas

from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

#define scraping function
def scrape_all():
    #initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)

    #run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    #stop webdriver and return data
    browser.quit()
    return data

#define mars news function
def mars_news(browser):

    #scrape mars news
    #visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    #optional delay for laoding the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #convert browser html to soup object and then quit browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        #use parent element to find first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        #use parent element to find paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p

#define featured image function
def featured_image(browser):
    #visit url
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    #find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    #parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #add try/except for error handling
    try:
        #find relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None

    #use base url to create absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

#define mars facts function
def mars_facts():
    #add try/except for error handling
    try:
        #use 'read_html' to scrape facts table into dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None
    
    #assign columns and set index of dataframe
    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    #convert dataframe into HTML format, add bootstrap
    return df.to_html(classes='table table-striped')

if __name__ == '__main__':

    #if running as script, print scraped data
    print(scrape_all())
    



