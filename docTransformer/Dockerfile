FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install Java and other necessary packages
RUN apt-get update && apt-get install -y \
    docker.io \
    openjdk-17-jdk \
    gcc \
    g++ \
    build-essential \
    ghostscript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME path to use konlpy library
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

# Download spaCy models
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download ko_core_news_sm

# USER django => unable to find user django
# Make port 80 available to the world outside this container
#EXPOSE 80
COPY . /app
# Run the Django application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8501"]
