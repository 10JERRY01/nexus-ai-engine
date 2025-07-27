# Nexus AI: A Conversational News and Analysis Engine

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/) [![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://www.docker.com/) [![GCP](https://img.shields.io/badge/Google_Cloud-Deployed-blue?logo=google-cloud)](https://cloud.google.com/run) [![Generative AI](https://img.shields.io/badge/Generative_AI-RAG_Pipeline-orange)](https://huggingface.co/transformers)

A complete, end-to-end system that automatically ingests and analyzes global news, allowing users to ask complex questions and receive AI-generated, evidence-based answers.

### **[View the Live Demo](https://nexus-ai-service-671408180579.us-central1.run.app)**

*(Note: The application is deployed on a serverless container. The first request may take a moment to "wake up" the instance.)*

---

## **Key Features**

*   **Automated Data Pipeline:** A Python service fetches news articles from live APIs and stores them in a local SQLite database.
*   **AI-Powered Analysis:** An NLP pipeline enriches each article with **Named Entity Recognition**, **Sentiment Analysis**, and **LLM-Generated Summaries**.
*   **Conversational Q&A:** Users can ask questions in natural language. A **Retrieval-Augmented Generation (RAG)** system finds relevant articles and uses a Generative AI model to synthesize a comprehensive answer with source citations.
*   **Production-Ready Deployment:** The entire application is containerized with a **multi-stage Dockerfile** to ensure fast startups and is deployed as a serverless application on **Google Cloud Run**.

For a complete technical breakdown, architecture diagrams, and design decisions, please see the full **[PROJECT DOCUMENTATION](./DOCUMENTATION.md)**.

## **Quick Start: Running Locally**

This project is fully containerized, so all you need is Docker.

**1. Clone the repository:**
git clone <your-repo-url>
cd nexus-ai
**2. Configure your News API key:
Create a file named config.py.
Add your key: NEWS_API_KEY = "YOUR_NEWS_API_KEY"
**3. Build and Run the Docker container:
The multi-stage build will automatically create and populate the database.
Generated bash
# Build the image (this will take time on the first run)
docker build -t nexus-ai-app .

# Run the container
docker run -d -p 8080:5000 --name nexus-ai-instance nexus-ai-app
Use code with caution.
Bash
4. Access the application:
Open your browser to http://localhost:8080.
Technology Showcase
This project was built to demonstrate proficiency across the full stack of a modern AI application:
Languages & Frameworks: Python, SQL, Flask, Gunicorn
AI & NLP:
Deep Learning: PyTorch
Generative AI / LLMs: Hugging Face transformers (FLAN-T5, BART)
Natural Language Processing: spaCy, TextBlob, Scikit-learn
Database: SQLite, SQLAlchemy ORM
DevOps & Cloud: Docker, Google Cloud Run, Google Artifact Registry
