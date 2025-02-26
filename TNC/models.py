from pydantic import BaseModel

# Define the Pydantic model with an extra field for recommended items.
class SearchResult(BaseModel):
    id: int
    url: str
    title: str
    date: str = ""
    content: str = ""
    recommended: bool = False
    
    
class NewsCard(BaseModel):
    image_url: str
    title: str
    excerpt: str
    byline: str
    
    
class EventCard(BaseModel):
    url: str
    date: str
    site: str
    title: str
    time: str
    description: str