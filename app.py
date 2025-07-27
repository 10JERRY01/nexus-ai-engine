# app.py

import logging
from flask import Flask, request, jsonify
from flask import Flask, request, jsonify, render_template
# --- Database Imports ---
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from aggregator import Article, ArticleAnalysis, DATABASE_URI

# --- AI and NLP Imports ---
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --- Basic Flask App Setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# =================================================================
#  GLOBAL SETUP (RUNS ONCE WHEN THE APP STARTS)
# =================================================================

# --- Database Connection ---
logging.info("Setting up database connection...")
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
db_session = Session()
logging.info("Database connection successful.")

# --- Load AI Models ---
logging.info("Loading text2text-generation pipeline...")
# Flan-T5 is an excellent model for instruction-following and Q&A
generator = pipeline('text2text-generation', model='google/flan-t5-base')
logging.info("AI models loaded successfully.")

# --- Data and Retriever Setup ---
logging.info("Loading articles and preparing the retriever...")
# Load all articles and their analyses from the database into memory
# joinedload() efficiently grabs the related analysis in the same query
all_articles = db_session.query(Article).options(joinedload(Article.analysis)).all()

# We'll use summaries for retrieval as they are dense and clean.
# Fallback to content if no summary is available.
retrieval_docs = [
    article.analysis.summary if article.analysis and article.analysis.summary else article.content
    for article in all_articles
]
retrieval_docs = [doc for doc in retrieval_docs if doc] # Ensure no None values

# Create and fit the TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
tfidf_matrix = vectorizer.fit_transform(retrieval_docs)
logging.info("Retriever is ready. Application startup complete.")

# =================================================================
#  CORE RAG LOGIC
# =================================================================

def process_question(question_text):
    """
    This is the main RAG function.
    """
    # 1. --- RETRIEVAL ---
    logging.info(f"Received question: '{question_text}'")
    logging.info("Step 1: Retrieving relevant documents...")
    
    # Vectorize the user's question using the same vectorizer
    question_vector = vectorizer.transform([question_text])
    
    # Calculate cosine similarity between the question and all articles
    cosine_similarities = cosine_similarity(question_vector, tfidf_matrix).flatten()
    
    # Get the indices of the top 3 most similar articles
    # We use argsort to get indices, then flip to get descending order
    top_n = 3
    relevant_indices = cosine_similarities.argsort()[-top_n:][::-1]
    
    # Get the actual article objects and their scores
    retrieved_articles = [all_articles[i] for i in relevant_indices]
    retrieved_scores = [cosine_similarities[i] for i in relevant_indices]

    logging.info(f"Found {len(retrieved_articles)} relevant articles.")
    for i, article in enumerate(retrieved_articles):
        logging.info(f"  - Relevance: {retrieved_scores[i]:.2f}, Title: {article.title}")

    # 2. --- AUGMENTATION ---
    logging.info("Step 2: Augmenting prompt with retrieved context...")

    # Create the context string by concatenating the content of retrieved articles
    context = "\n\n---\n\n".join([
        f"Article Title: {art.title}\nArticle Content: {art.content}"
        for art in retrieved_articles
    ])

    # This is our prompt template. It's crucial for instructing the LLM.
    prompt = f"""
    Please act as a helpful AI news analyst.
    Answer the following question based ONLY on the context provided below.
    If the context does not contain the answer, please state that you cannot answer based on the provided information.

    CONTEXT:
    {context}

    QUESTION:
    {question_text}

    ANSWER:
    """

    # 3. --- GENERATION ---
    logging.info("Step 3: Generating answer with LLM...")
    generated_text = generator(prompt, max_length=512, num_beams=4, early_stopping=True)
    answer = generated_text[0]['generated_text']
    logging.info(f"Generated Answer: {answer}")
    
    # Prepare the sources to send back to the user
    sources = [
        {"title": art.title, "url": art.url} for art in retrieved_articles
    ]
    
    return {
        "answer": answer,
        "sources": sources
    }
# =================================================================
#  FRONTEND ROUTE
# =================================================================
@app.route('/')
def index():
    """Serves the main HTML user interface."""
    return render_template('index.html')
# =================================================================
#  FLASK API ENDPOINT
# =================================================================

@app.route('/ask', methods=['POST'])
def ask_endpoint():
    """ The main API endpoint """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"error": "JSON payload must include a 'question' key"}), 400

    try:
        result = process_question(question)
        return jsonify(result)
    except Exception as e:
        logging.error(f"An error occurred during question processing: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

# =================================================================
#  MAIN EXECUTION
# =================================================================

if __name__ == '__main__':
    # Setting debug=False because the auto-reloader can cause issues
    # with loading models twice. For development, it's better to
    # manually stop and start the server when you make changes.
    app.run(host='0.0.0.0', port=5000, debug=False)

