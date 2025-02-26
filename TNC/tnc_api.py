import http.client
import json
from urllib.parse import quote_plus
from typing import List
from bs4 import BeautifulSoup
import streamlit as st
from .models import SearchResult, NewsCard, EventCard

    
def _extract_search_results(html_content: str) -> List[dict]:
    """
    Parses the HTML content and extracts search result items.

    This function looks for <li> elements with the class "c-search-result-item"
    (including those marked as "recommendedItem") and extracts:
      - url: from the <a> tag's href attribute.
      - title: from the <h3> element text or the <a> tag's title attribute.
      - date: from the <span> with the date class (if available).
      - content: from the <p> element with the content class.
      - recommended: a boolean flag indicating if this item is marked as recommended.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Select all <li> elements with the class "c-search-result-item"
    items = soup.select("li.c-search-result-item")
    
    results = []
    for li in items:
        # Check if this item is a recommended item.
        classes = li.get("class", [])
        recommended = "recommendedItem" in classes
        
        # Extract the <a> tag for URL and title.
        a_tag = li.find("a")
        if a_tag:
            url = a_tag.get("href", "").strip()
            h3_tag = a_tag.find("h3", class_="c-search-result-item__title")
            title = h3_tag.get_text(strip=True) if h3_tag else a_tag.get("title", "").strip()
        else:
            url, title = "", ""
        
        # Extract the date from the <span> tag if present.
        date_span = li.find("span", class_="c-search-result-item__date")
        date_text = date_span.get_text(strip=True) if date_span else ""
        
        # Extract the content from the <p> tag.
        p_tag = li.find("p", class_="c-search-result-item__content")
        content_text = p_tag.get_text(strip=True) if p_tag else ""
        
        results.append({
            "id": items.index(li),
            "url": url,
            "title": title,
            "date": date_text,
            "content": content_text,
            "recommended": recommended
        })
    
    return results

def get_search_results(query: str) -> List[SearchResult]:
    """
    Given a search query string, this function:
      1. Constructs a URL-encoded search URL for Nature.org.
      2. Uses the ScrapingAnt API to retrieve the HTML page.
      3. Parses the HTML to extract search result details.
      4. Returns a list of SearchResult Pydantic objects.
    """
    # URL-encode the query.
    encoded_query = quote_plus(query)
    base_search_url = f"https://www.nature.org/en-us/search/?q={encoded_query}"
    
    # API key for ScrapingAnt (example key).
    api_key = st.secrets["SCRAPINGANT_API_KEY"]
    api_path = f"/v2/general?url={base_search_url}&x-api-key={api_key}"
    
    # Retrieve HTML content from the API.
    conn = http.client.HTTPSConnection("api.scrapingant.com")
    
    http.client._MAXHEADERS = 1000 

    conn.request("GET", api_path)
    res = conn.getresponse()
    data = res.read()
    
    html_content = data.decode("utf-8")
    
    # Extract search results as a list of dictionaries.
    results_dict = _extract_search_results(html_content)
    
    # Convert each dictionary to a Pydantic object.
    return [SearchResult(**item) for item in results_dict]


def _extract_news_cards(html_content: str) -> List[dict]:
    """
    Parses the HTML content and extracts news card items.

    This function looks for the main container with class "cards-container bs_row"
    and then extracts all news cards with class "c-cards-press-release__card-container border-primary".
    For each card, it extracts:
      - image_url: from the <img> tag's src attribute within the <picture> element.
      - title: from the <h4> element with class "c-cards-press-release__title".
      - excerpt: from the <p> element with class "c-cards-press-release__excerpt".
      - byline: from the <p> element with class "c-cards-press-release__byline".
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find the main container of news cards
    container = soup.find("div", class_="cards-container bs_row")
    if not container:
        return []
    
    # Select all card containers
    cards = container.find_all("div", class_="c-cards-press-release__card-container border-primary")
    
    results = []
    for card in cards:
        # Extract image URL from the <img> tag inside <picture>
        img_tag = card.find("img", class_="c-cards-press-release__image")
        image_url = img_tag.get("src", "").strip() if img_tag else ""
        
        # Extract the title from the <h4> element
        title_tag = card.find("h4", class_="c-cards-press-release__title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        
        # Extract the excerpt from the appropriate <p> element
        excerpt_tag = card.find("p", class_="c-cards-press-release__excerpt")
        excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else ""
        
        # Extract the byline (which includes location and date)
        byline_tag = card.find("p", class_="c-cards-press-release__byline")
        byline = byline_tag.get_text(strip=True) if byline_tag else ""
        
        results.append({
            "image_url": image_url,
            "title": title,
            "excerpt": excerpt,
            "byline": byline
        })
    
    return results

def get_news_cards(query: str) -> List[NewsCard]:
    """
    Given a search query string, this function:
      1. Constructs a URL-encoded news search URL.
      2. Uses the ScrapingAnt API to retrieve the HTML page.
      3. Parses the HTML to extract news card details.
      4. Returns a list of NewsCard Pydantic objects.
    """
    # URL-encode the query.
    encoded_query = quote_plus(query)
    base_news_url = f"https://www.nature.org/en-us/newsroom/?press_q={encoded_query}"
    
    # API key for ScrapingAnt (example key).
    api_key = st.secrets["SCRAPINGANT_API_KEY"]
    api_path = f"/v2/general?url={base_news_url}&x-api-key={api_key}"
    
    # Retrieve HTML content from the API.
    conn = http.client.HTTPSConnection("api.scrapingant.com")
    
    http.client._MAXHEADERS = 1000 

    conn.request("GET", api_path)
    res = conn.getresponse()
    data = res.read()
    html_content = data.decode("utf-8")
    
    # Extract news cards as a list of dictionaries.
    results_dict = _extract_news_cards(html_content)
    
    # Convert each dictionary to a Pydantic NewsCard object.
    return [NewsCard(**item) for item in results_dict]



def event_search(region: str, key_word: str):
    return [
        EventCard(
            url="https://www.nature.org/en-us/get-involved/how-to-help/events/colorado-mountainfilm-on-tour/",
            title="Mountainfilm on Tour",
            description="Please join us at the Denver Museum of Nature & Science for an evening of conservation and science-focused short films, panel discussions, and treats!",
            date="Mar 05, 2025",
            site='Denver',
            time='6:00 PM - 9:00 PM'
        ),
        EventCard(
            url="https://www.nature.org/en-us/get-involved/how-to-help/events/utah-ski-for-nature/",
            title="2025 Annual Meeting",
            description="Join us for our annual meeting where we will discuss our progress, challenges, and future plans for conservation in 2025.",
            date="Apr 12, 2025",
            site='New York',
            time='10:00 AM - 1:00 PM'
        ),
        EventCard(
            url="https://www.nature.org/en-us/get-involved/how-to-help/events/tx-davis-mountains-open-days/",
            title="2025 Annual Meeting",
            description="Join us for our annual meeting where we will discuss our progress, challenges, and future plans for conservation in 2025.",
            date="Apr 12, 2025",
            site='New York',
            time='10:00 AM - 1:00 PM'
        ),
        EventCard(
            url="https://www.nature.org/en-us/get-involved/how-to-help/events/west-texas-springs-preserve-tours/",
            title="2025 Annual Meeting",
            description="Join us for our annual meeting where we will discuss our progress, challenges, and future plans for conservation in 2025.",
            date="Apr 12, 2025",
            site='New York',
            time='10:00 AM - 1:00 PM'
        ),   
    ]

