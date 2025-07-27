# analysis_pipeline.py

import spacy
from textblob import TextBlob
import logging
import json
from transformers import pipeline
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Import our database models and config from the other script
from aggregator import Article, ArticleAnalysis, DATABASE_URI

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Database Setup ---
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# --- Load NLP Model ---
# Load the small English model we downloaded
# Disable components we don't need for speed
nlp = spacy.load("en_core_web_sm", disable=["parser", "lemmatizer"])
logging.info("spaCy NLP model loaded.")
logging.info("Loading summarization pipeline...")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
logging.info("Summarization pipeline loaded.")


def analyze_article_content(text):
    """
    Performs NER and Sentiment Analysis on a given text.
    Returns a dictionary with the analysis results.
    """
    if not text or not isinstance(text, str):
        return {
            "entities": [],
            "polarity": 0.0,
            "subjectivity": 0.0
        }

    # --- Sentiment Analysis with TextBlob ---
    blob = TextBlob(text)
    sentiment = blob.sentiment  # Returns a tuple (polarity, subjectivity)

    # --- Named Entity Recognition with spaCy ---
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        # We only care about specific entity types
        if ent.label_ in ["PERSON", "ORG", "GPE"]: # GPE = Geopolitical Entity (countries, cities)
            entities.append({"text": ent.text, "label": ent.label_})

    return {
        "entities": entities,
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity
    }


# Replace the entire main() function in analysis_pipeline.py

def main():
    """
    Main function to process articles: runs analysis and generates summaries.
    """
    # A more robust query: find articles that either have no analysis record
    # OR have one that is missing a summary. This makes the script re-runnable.
    articles_to_process = session.query(Article).outerjoin(ArticleAnalysis).filter(
        (ArticleAnalysis.id == None) | (ArticleAnalysis.summary == None)
    ).all()

    if not articles_to_process:
        logging.info("No new articles to analyze or summarize. Everything is up to date.")
        return

    logging.info(f"Found {len(articles_to_process)} articles to process.")
    
    for article in articles_to_process:
        # Check if an analysis record already exists or if we need a new one
        analysis_record = article.analysis
        if not analysis_record:
            logging.info(f"Performing initial analysis for article ID: {article.id}")
            analysis_record = ArticleAnalysis(article_id=article.id)
            
            # Perform NER and Sentiment only if it's a new record
            analysis_results = analyze_article_content(article.content)
            analysis_record.named_entities = json.dumps(analysis_results["entities"])
            analysis_record.sentiment_polarity = analysis_results["polarity"]
            analysis_record.sentiment_subjectivity = analysis_results["subjectivity"]
            session.add(analysis_record)

        # --- Summarization Step ---
        # Check if a summary is missing and if there's content to summarize
        if not analysis_record.summary and article.content:
            logging.info(f"Generating summary for article ID: {article.id}...")
            try:
                # BART model has a max input length of 1024 tokens
                # We truncate the article content to be safe
                input_text = article.content[:1024] 
                
                summary_result = summarizer(input_text, max_length=150, min_length=40, do_sample=False)
                
                generated_summary = summary_result[0]['summary_text']
                analysis_record.summary = generated_summary
                logging.info(f"Summary generated for article ID: {article.id}")

            except Exception as e:
                logging.error(f"Could not generate summary for article ID {article.id}: {e}")

    # Commit all changes (new analyses and new summaries) to the database
    session.commit()
    logging.info("Pipeline run complete. All changes have been saved to the database.")
    
    session.close()


if __name__ == "__main__":
    main()