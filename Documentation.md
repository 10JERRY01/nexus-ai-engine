Nexus AI: A Conversational News and Analysis Engine
![alt text](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![alt text](https://img.shields.io/badge/Docker-25-blue?logo=docker)
![alt text](https://img.shields.io/badge/Google_Cloud-Deployed-blue?logo=google-cloud)
![alt text](https://img.shields.io/badge/Generative_AI-LLM-orange)
![alt text](https://img.shields.io/badge/NLP-spaCy-orange)
![alt text](https://img.shields.io/badge/Database-SQLite-lightgrey)
Live Demo URL: https://nexus-ai-service-671408180579.us-central1.run.app
(Note: The first request to the live demo may be slow due to the "cold start" of the container.)
Project Mission
Inspired by Google's mission to "organize the world's information and make it universally accessible and useful," Nexus AI is a comprehensive, end-to-end system that automatically gathers global news, enriches it with AI-driven analysis, and allows users to have natural language conversations about the data.
This project demonstrates a full lifecycle of a modern AI application, from data ingestion and processing to model serving and cloud deployment, showcasing proficiency in Python, SQL, Deep Learning, NLP, Generative AI (LLMs), and cloud infrastructure.
Core Features
Automated News Aggregation: A Python service automatically fetches the latest news articles about technology and AI from a live news API.
AI-Powered Data Enrichment: Each article is processed through an NLP pipeline that performs:
Named Entity Recognition (NER): Identifies and extracts key entities like organizations, people, and places.
Sentiment Analysis: Determines the emotional tone of the article.
AI-Generated Summaries: Utilizes a Large Language Model (LLM) to generate concise, abstractive summaries.
Conversational Search (RAG): The core feature is a conversational API built on a Retrieval-Augmented Generation (RAG) architecture. Users can ask complex questions in plain English. The system retrieves the most relevant articles from its database and uses a Generative AI model to synthesize a coherent, evidence-based answer, complete with source links.
Containerized & Cloud-Deployed: The entire application is containerized using Docker and deployed on Google Cloud Run, making it scalable, portable, and publicly accessible.
Tech Stack & Architecture
Component	Technology / Library	Purpose
Backend	Python 3.12	Core application logic.
Web Server	Flask, Gunicorn	To serve the API and frontend UI. Gunicorn is used as the production-grade WSGI server.
Database	SQLite	For storing articles and their corresponding AI analysis results.
DB Interaction	SQLAlchemy	ORM for robust and maintainable database interactions.
NLP Analysis	spaCy, TextBlob	For Named Entity Recognition and Sentiment Analysis.
Generative AI	Hugging Face transformers, PyTorch	For LLM-powered summarization (facebook/bart-large-cnn) and Q&A (google/flan-t5-base).
Retrieval	Scikit-learn	For TfidfVectorizer and Cosine Similarity to find articles relevant to a user's question.
Containerization	Docker	To package the application and its dependencies into a portable image.
Deployment	Google Cloud Run, Google Artifact Registry	To host the containerized application, making it a scalable, serverless, and publicly available service.
Architectural Flow
The system operates in two main phases: an offline data processing pipeline and an online inference API.
1. Data Processing (Handled in the Docker build process):
News API -> Python Aggregator -> SQLite DB -> NLP/LLM Pipeline -> Enriched SQLite DB
2. Conversational API (Handled by the live Cloud Run service):
User Query -> TF-IDF Retriever -> Relevant Docs -> LLM (RAG) -> Synthesized Answer
Project Structure
Generated code
nexus-ai/
├── templates/
│   └── index.html         # Simple frontend UI
├── aggregator.py          # Script to fetch and store news articles
├── analysis_pipeline.py   # Script for NLP analysis and summarization
├── app.py                 # Main Flask application with the /ask endpoint
├── config.py              # Configuration for API keys and database
├── Dockerfile             # Multi-stage Dockerfile for production builds
├── Documentation.md       # This file
└── requirements.txt       # Python package dependencies
Use code with caution.
Setup and Execution
Prerequisites
Git
Docker Desktop
Google Cloud SDK (gcloud)
1. Running Locally
Clone the repository:
Generated bash
git clone <your-repo-url>
cd nexus-ai
Use code with caution.
Bash
Configure API Key:
Rename config.py.template to config.py (or create it).
Add your NewsAPI key to config.py:
Generated python
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
Use code with caution.
Python
Build the Docker Image:
This will run the multi-stage build, which includes creating and populating the database.
Generated bash
docker build -t nexus-ai-app .
Use code with caution.
Bash
Run the Container:
Generated bash
docker run -d -p 8080:5000 --name nexus-ai-instance nexus-ai-app
Use code with caution.
Bash
Access the Application:
Open your browser and navigate to http://localhost:8080.
2. Cloud Deployment on GCP
The application is deployed on Google Cloud Run. The high-level steps are:
Push the Docker Image: The built image is pushed to Google Artifact Registry.
Generated bash
# (After authentication and tagging)
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/nexus-ai-repo/nexus-ai-app:latest
Use code with caution.
Bash
Deploy the Service: The image is deployed using a gcloud command, with memory, CPU, and timeout settings appropriate for a memory-intensive AI application.
Generated bash
gcloud run deploy nexus-ai-service \
  --image=<image-url> \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=5000 \
  --memory=4Gi --cpu=2 --timeout=600s
Use code with caution.
Bash
Key Technical Decisions & Trade-offs
Production-Ready Containerization: A multi-stage Dockerfile is used to solve the "cold start" timeout problem on Cloud Run. The first "builder" stage does all the heavy, one-time data processing to create a populated SQLite database. The final "runner" stage is a lean container that simply copies this pre-built database and the application code, ensuring a much faster startup time suitable for a serverless environment.
Retrieval-Augmented Generation (RAG): Instead of simply using a generic LLM, a RAG architecture was implemented. This grounds the AI's responses in factual data retrieved from the project's own database, reducing hallucinations and allowing the system to cite its sources.
Deployment Strategy (CPU vs. GPU): The current live deployment uses a CPU instance on Cloud Run to leverage the free tier and demonstrate cost-effective deployment for a web service. However, the project is built to be "GPU-ready" and can be deployed to a GPU-enabled service like Google Vertex AI Endpoints for significantly higher performance on AI inference tasks. This reflects an understanding of the trade-offs between cost, performance, and infrastructure choice.
Future Enhancements
GPU-Accelerated Deployment: Deploy the container to a GPU-enabled service like Vertex AI Endpoints to drastically reduce inference latency.
Vector Database Retrieval: Replace the TF-IDF retrieval system with a more advanced vector database (e.g., Pinecone, Chroma, or PostgreSQL with pgvector) for more semantically powerful document retrieval.
Real-time Data Pipeline: Integrate a message queue (like RabbitMQ or Kafka) to make the news aggregation and analysis a real-time, event-driven process.
Frontend Framework: Rebuild the frontend using a modern framework like React or Vue.js for a richer user experience.