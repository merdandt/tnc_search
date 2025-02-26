import http.client
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import streamlit as st
import TNC.tnc_api as tnc

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_media_accounts",
            "description": "Returns the public URLs for different TNC's social media accounts to follow, interact, or get updates.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_website_structure",
            "description": "Returns the structure of TNC's website with the main sections, subsections and external URLs. For more informed decisions and navigation regarding user requests.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "visit_any_web_site",
            "description": "Visit any website and returns the string representation of the web page under the given URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "String representation of the URL to visit."
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_TNC_knowledge_base",
            "description": "Key word search! Searches TNC's knowledge base for articles containing the query. This function is the main source of information about TNC's initiatives, projects, reports and anything else.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for in the knowledge base."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "event_search",
            "description": "Searches for events regarding TNC in a specific region containing a specific keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "The region to search for events."
                    },
                    "key_word": {
                        "type": "string",
                        "description": "The keyword to search for in the event description."
                    }
                },
                "required": ["region", "key_word"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "news_search",
            "description": "Searches for news headlines containing the query key word regarding TNC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for in the news articles."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def get_media_accounts():
    """Returns the public URLs for different TNC's social media accounts to follow, interact, or get updates.
    
    Returns:
        dict: A dictionary containing the URLs for TNC's social media accounts.
    """
    return  {
        "facebook": "https://www.facebook.com/thenatureconservancy/",
        "twitter": "https://x.com/nature_org",
        "linkedin": "https://www.linkedin.com/company/the-nature-conservancy/",
        "instagram": "https://www.instagram.com/nature_org/?hl=en",
        "youtube": "https://www.youtube.com/user/natureconservancy",
        "tiktok": "https://www.tiktok.com/@thenatureconservancy",
    }  
    
def get_website_structure():
    """Returns the structure of TNC's website with the main sections, subsections and external URLs. For more informed decisions and navigation regarding user requests.
    
    Returns:
        dict: A dictionary containing the structure of TNC's website.
    """
    return {
        "Nature Conservancy Website Structure": {
          "Homepage": {
            "URL": "https://www.nature.org/en-us/",
            "Sections": [
              "Donate",
              "What We Do",
              "About Us",
              "Get Involved",
              "Membership & Giving"
            ]
          },
          "Main Sections": {
            "Donate": {
              "URL": "https://www.nature.org/en-us/donateredirect/support-nature/"
            },
            "What We Do": {
              "Subpages": {
                "Our Priorities": [
                  {
                    "Title": "Tackle Climate Change",
                    "URL": "https://www.nature.org/en-us/what-we-do/our-priorities/tackle-climate-change/"
                  },
                  {
                    "Title": "Protect Ocean, Land & Fresh Water",
                    "URL": "https://www.nature.org/en-us/what-we-do/our-priorities/protect-water-and-land/"
                  },
                  {
                    "Title": "Provide Food and Water",
                    "URL": "https://www.nature.org/en-us/what-we-do/our-priorities/provide-food-and-water-sustainably/"
                  }
                ],
                "Our Insights": [
                  {
                    "Title": "Perspectives",
                    "URL": "https://www.nature.org/en-us/what-we-do/our-insights/perspectives/"
                  },
                  {
                    "Title": "Reports",
                    "URL": "https://www.nature.org/en-us/what-we-do/our-insights/reports/"
                  },
                  {
                    "Title": "Data & Tools",
                    "URL": "https://www.nature.org/en-us/what-we-do/our-insights/data-and-tools/"
                  }
                ]
              }
            },
            "About Us": {
              "Subpages": {
                "Who We Are": [
                  {
                    "Title": "Our People",
                    "URL": "https://www.nature.org/en-us/about-us/who-we-are/our-people/"
                  },
                  {
                    "Title": "Our Science",
                    "URL": "https://www.nature.org/en-us/about-us/who-we-are/our-science/"
                  },
                  {
                    "Title": "Our Accountability",
                    "URL": "https://www.nature.org/en-us/about-us/who-we-are/accountability/"
                  },
                  {
                    "Title": "How We Work",
                    "URL": "https://www.nature.org/en-us/about-us/who-we-are/how-we-work/"
                  },
                  {
                    "Title": "Our History",
                    "URL": "https://www.nature.org/en-us/about-us/who-we-are/our-history/"
                  }
                ],
                "Where We Work": [
                  {
                    "Title": "Africa",
                    "URL": "https://www.nature.org/en-us/about-us/where-we-work/africa/"
                  },
                  {
                    "Title": "Asia Pacific",
                    "URL": "https://www.nature.org/en-us/about-us/where-we-work/asia-pacific/"
                  },
                  {
                    "Title": "Canada",
                    "URL": "https://www.nature.org/en-us/about-us/where-we-work/canada/"
                  }
                ]
              }
            },
            "Get Involved": {
              "Subpages": {
                "How To Help": [
                  {
                    "Title": "Volunteer",
                    "URL": "https://www.nature.org/en-us/get-involved/how-to-help/volunteer/"
                  },
                  {
                    "Title": "Attend Events",
                    "URL": "https://www.nature.org/en-us/get-involved/how-to-help/events/"
                  },
                  {
                    "Title": "Take Action",
                    "URL": "https://preserve.nature.org/page/80352/action/1"
                  },
                  {
                    "Title": "Calculate Your Carbon Footprint",
                    "URL": "https://www.nature.org/en-us/get-involved/how-to-help/carbon-footprint-calculator/"
                  }
                ]
              }
            },
            "Membership & Giving": {
              "Subpages": {
                "Donate": "https://www.nature.org/en-us/membership-and-giving/donate-to-our-mission/",
                "Become a Member": "https://www.nature.org/en-us/membership-and-giving/donate-to-our-mission/become-a-member/",
                "Renew": "https://www.nature.org/en-us/membership-and-giving/donate-to-our-mission/renew-membership/",
                "Give Monthly": "https://www.nature.org/en-us/membership-and-giving/donate-to-our-mission/give-monthly/"
              }
            }
          }
        }
    }   
       
def visit_any_web_site(url: str):
    """Visit any website and returns the string (utf-8) representation of the web page under the given URL.
    
    Args:
        url (str): String representation of the URL to visit.
        
    Returns:
        str: String representation of the web page under the given URL.
    """

    conn = http.client.HTTPSConnection("api.scrapingant.com")
    api_key = st.secrets["SCRAPINGANT_API_KEY"]

    conn.request("GET", f"/v2/general?url={url}&x-api-key={api_key}")

    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")  
  
def search_TNC_knowledge_base(query: str):
    """Key word search! Searches TNC's knowledge base for articles containing the query. This function is the main source of information about TNC's initiatives, projects, reports and anything else.
    
    Args:
        query (str): The query to search for in the knowledge base.
        
    Returns:
        List[dict]: A list of dictionaries containing the article details.
    """
    
    search_results = tnc.get_search_results(query)
    
    return search_results  
   
def event_search(region: str, key_word: str):
    """Searches for events regarding TNC in a specific region containing a specific keyword.
    
    Args:
        region (str): The region to search for events.
        key_word (str): The keyword to search for in the event description.
        
    Returns:
        List[dict]: A list of dictionaries containing the event details.
    """
    
    search_results = tnc.event_search(region, key_word)
    
    return search_results
      
def news_search(query: str):
    """Searches for news headlined containing the query key word regarding TNC.
    
    Args:
        query (str): The query to search for in the news articles.
        
    Returns:
        List[dict]: A list of dictionaries containing the news article details.
    """
    
    search_results = tnc.get_news_cards(query)
    
    return search_results