# aggregator.py

import requests
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine, ForeignKey
from datetime import datetime
import logging

# Import our configuration settings
from config import NEWS_API_KEY, DATABASE_URI

# Set up basic logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# This is the base class which our ORM class will inherit
Base = declarative_base()

# Define the Article class which maps to the 'articles' table
class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    source_name = Column(String(100))
    author = Column(String(100))
    url = Column(Text, nullable=False, unique=True)
    published_at = Column(DateTime)
    content = Column(Text)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    analysis = relationship("ArticleAnalysis", uselist=False, back_populates="article")
    def __repr__(self):
        return f"<Article(title='{self.title}')>"

# This goes right after the Article class definition
class ArticleAnalysis(Base):
    __tablename__ = 'article_analysis'

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False, unique=True)
    named_entities = Column(Text)  # Storing as JSON string
    sentiment_polarity = Column(sqlalchemy.Float)
    sentiment_subjectivity = Column(sqlalchemy.Float)
    summary = Column(Text)
    # This creates a back-reference from the Article class
    article = relationship("Article", back_populates="analysis")

# Add the corresponding relationship to the Article class
# This line should be added INSIDE the Article class definition
Article.analysis = relationship("ArticleAnalysis", uselist=False, back_populates="article")

# --- Database Engine and Session ---
# The engine is the entry point to our database.
engine = create_engine(DATABASE_URI)

# The Session is our handle for all database conversations.
Session = sessionmaker(bind=engine)
session = Session()

def fetch_news(api_key, query="Google AI"):
    """Fetches news articles from the News API."""
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': query,
        'language': 'en',
        'sortBy': 'publishedAt',
        'apiKey': api_key,
        'pageSize': 100  # Fetch the max allowed per request
    }
    try:
        logging.info(f"Fetching news for query: '{query}'")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        logging.info(f"Successfully fetched {len(data.get('articles', []))} articles.")
        return data.get('articles', [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news: {e}")
        return None


def main():
    """Main function to run the news aggregation process."""
    # Create the table in the database if it doesn't exist yet
    # This will create the 'nexus_database.db' file on the first run
    Base.metadata.create_all(engine)
    logging.info("Database table 'articles' created or already exists.")

    articles = fetch_news(NEWS_API_KEY, query="Generative AI OR Large Language Models")

    if not articles:
        logging.warning("No articles fetched. Exiting.")
        return

    articles_added = 0
    for item in articles:
        # Check if an article with the same URL already exists
        exists = session.query(Article).filter_by(url=item['url']).first()
        if exists:
            logging.info(f"Article '{item['title']}' already exists. Skipping.")
            continue

        # Convert publishedAt string to a datetime object
        published_time = datetime.fromisoformat(item['publishedAt'].replace('Z', '+00:00'))

        # Create a new Article object
        new_article = Article(
            title=item['title'],
            source_name=item['source']['name'],
            author=item['author'],
            url=item['url'],
            published_at=published_time,
            content=item['content']
        )
        # Add the new article to the session
        session.add(new_article)
        articles_added += 1

    # Commit the session to save all new articles to the database
    if articles_added > 0:
        session.commit()
        logging.info(f"Successfully added {articles_added} new articles to the database.")
    else:
        logging.info("No new articles to add.")

    # Always close the session
    session.close()

if __name__ == "__main__":
    main()