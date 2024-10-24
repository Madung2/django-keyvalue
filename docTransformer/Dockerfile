FROM python:3.12-slim

# Install Java and other necessary packages
RUN apt-get update && apt-get install -y \
    docker.io \
    openjdk-17-jdk \
    vim \
    gcc \
    g++ \
    build-essential \
    ghostscript \
    libmagic \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME path to use konlpy library
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

# Install Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

# Download spaCy models
RUN pip install --no-cache-dir numpy==1.23.5 thinc==8.1.8
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download ko_core_news_sm

COPY . /app

# Run the Django application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8501"]
