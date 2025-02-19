import requests
from langdetect import detect
from pymongo import MongoClient
from datetime import datetime
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

API_KEY = "ef8596fe84a2432e92429798bb560373"

def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False  

def fetch_news(category, num_articles=5, date=None):
    url = f'https://newsapi.org/v2/everything?q={category}&apiKey={API_KEY}&pageSize=10&sortBy=publishedAt'
    if date:
        url += f'&from={date}&to={date}'
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json()
        english_articles = [
            article for article in news_data['articles']
            if is_english(article['title'] + " " + (article['description'] or ""))
        ]
        return {"articles": english_articles[:num_articles]} 
    return None

def create_db():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["news_agent"]
        return db["news_data"]
    except Exception:
        return None

news_collection = create_db()

def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 1)
    return str(summary[0]) if summary else text[:150] + "..."

def save_news_data(category, num_articles=5, date=None):
    news_data = fetch_news(category, num_articles, date)
    if not news_data:
        return "Failed to fetch news."
    
    day = date if date else datetime.now().strftime("%Y-%m-%d")
    for article in news_data["articles"]:
        title = article["title"] or ""
        description = article["description"] or ""
        if not title and not description:
            continue  
        summary = summarize_text(description)
        document = {
            "category": category,
            "day": day,
            "title": title,
            "description": description,
            "summary": summary
        }
        news_collection.insert_one(document)
    return f"Saved {len(news_data['articles'])} articles."

def get_summaries(category, date):
    articles = list(news_collection.find({"category": category, "day": date}, {"_id": 0, "title": 1, "summary": 1}))
    if not articles:
        return "No summaries found."
    return "\n".join(f"- **{article['title']}**: {article['summary']}" for article in articles)
