# --- Stage 1: The "Builder" ---
# Use Python 3.10, which matches your local environment
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aggregator.py .
COPY analysis_pipeline.py .
COPY config.py .

RUN python aggregator.py
RUN python analysis_pipeline.py


# --- Stage 2: The "Runner" ---
# This is the final, lean image that will be deployed.
FROM python:3.12-slim

WORKDIR /app

# Copy only the requirements file first
COPY requirements.txt .
RUN pip install --no-cache-dir --no-deps -r requirements.txt
RUN pip install gunicorn

# --- START OF THE FIX ---
# Copy the application code that needs to run.
# We need app.py, and we ALSO need the files it imports from!
COPY app.py .
COPY aggregator.py .
COPY config.py .
# --- END OF THE FIX ---

# This is the magic step: Copy the fully populated database
# from the "builder" stage into this final stage.
COPY --from=builder /app/nexus_database.db .

ENV HF_HOME="/app/huggingface_cache"
RUN mkdir -p $HF_HOME

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]