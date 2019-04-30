import time
import re
from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd
import requests
from selenium import webdriver
import pymongo
from sys import platform

def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=True)

def get_mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')
    title_tags = soup.find_all('div', class_='content_title')
    # for some reason soup.find was not returning the most recent so
    # get the first element in the list of content titles. 
    news = title_tags[0]
    # next item is the teaser body
    news_title = news.get_text()
    teaser = news.next_sibling
    news_p = teaser.get_text()
    return (news_title, news_p)

def get_featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    browser.click_link_by_partial_text('FULL IMAGE')
    # wait for the page to load
    time.sleep(2)
    browser.click_link_by_partial_text('more info')
    # wait for the page to load
    time.sleep(2)
    browser.click_link_by_partial_text('.jpg') 
    html = browser.html
    soup = bs(html, 'html.parser')

    featured_img_url = soup.find('img').get('src')
    return featured_img_url

def get_weather_tweet(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    html = browser.html

    soup = bs(html, "html.parser")
    tweets = soup.find_all("p", "TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")

    #get the first tweet
    return tweets[0].get_text()
    

def get_planet_facts():
    url = 'https://space-facts.com/mars/'
    table_df = pd.read_html(url)[0]
    table_df = table_df.rename(columns={0:'Mars Planet Profile', 1:''})
    table_df = table_df.set_index('Mars Planet Profile', drop=True)
    table = table_df.to_html(classes = 'table table-striped')
    return table

def find_hemisphere_name(link_text):
    end_index = link_text.find("Enhanced", 0)
    #take the string up to the index right before "Enhanced"
    return link_text[0:(end_index - 1)]

def get_hemisphere_data(browser):
    base_url = 'https://astrogeology.usgs.gov'
    list_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(list_url)

    list_html = browser.html
    soup = bs(list_html, 'html.parser')

    hem_img_urls = []

    links = soup.find_all('a', class_="itemLink product-item")

    for link in links:
    #there are links with no text in the html body that are duplicates of the "Enhanced" links, 
        link_text = link.get_text()
        if "Enhanced" in link_text:
            sub_url = f"{base_url}{link.get('href')}"
            
            hem_name = find_hemisphere_name(link_text)
            
            #visit the page for this hemisphere and load its HTML
            browser.visit(sub_url)
            sub_soup = bs(browser.html, 'html.parser')
            
            # find the link to the high def image by finding the link that says "Sample" on the page
            sample_link = sub_soup.find("a", string="Sample")
            sample_image_url = sample_link.get("href")
            
            # add the results to our url list
            hem_dict = {}
            hem_dict["title"] = hem_name
            hem_dict["img_url"] = sample_image_url
            hem_img_urls.append(hem_dict)
    
    return hem_img_urls


def scrape():
    browser = init_browser()
    mars_data_scrape = {}

    #fetch news
    mars_news = {}
    news_title, news_p = get_mars_news(browser) 
    mars_news["title"] = news_title
    mars_news["preview"] = news_p
    mars_data_scrape["news"] = mars_news

    #fetch featured image
    featured_image = get_featured_image(browser)
    mars_data_scrape["featured_image"] = featured_image

    #fetch most recent weather tweet
    weather_tweet = get_weather_tweet(browser)
    mars_data_scrape["weather"] = weather_tweet

    #fetch planet facts html
    facts = get_planet_facts()
    mars_data_scrape["facts_table"] = facts

    hemispheres = get_hemisphere_data(browser)
    mars_data_scrape["hemismphere_images"] = hemispheres

    return mars_data_scrape