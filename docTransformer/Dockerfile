
# FROM python:3.12-slim
# # We had issue with 3.12 compatibility with numpy and thinc
# # python11 은 poetry에서 먼저 막힘...

# # Install Java and other necessary packages
# RUN apt-get update && apt-get install -y \
#     docker.io \
#     openjdk-17-jdk \
#     vim \
#     gcc \
#     g++ \
#     build-essential \
#     ghostscript \
#     #python3-tk \
#     #poppler-utils\
#     libmagic-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Set JAVA_HOME path to use konlpy library
# ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64
# ENV PATH $JAVA_HOME/bin:$PATH

# # Install Poetry
# RUN pip install --no-cache-dir poetry

# WORKDIR /app
# COPY pyproject.toml poetry.lock /app/


# # Install Python dependencies using Poetry
# RUN poetry config virtualenvs.create false
# RUN poetry install --no-interaction --no-ansi

# # Download spaCy models
# # RUN pip install --no-cache-dir numpy==1.23.5 thinc==8.1.8 
# RUN pip install --no-cache-dir numpy thinc 
# RUN pip install --no-cache-dir camelot-py[base] opencv-python-headless
# #RUN python -m spacy download en_core_web_sm
# #RUN python -m spacy download ko_core_news_sm

# COPY . /app

# # Run the Django application
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8501"]
FROM python:3.11-slim

# Install Java and other necessary packages
RUN apt-get update && apt-get install -y \
    libreoffice \
    unoconv \
    docker.io \
    openjdk-17-jdk \
    vim \
    gcc \
    g++ \
    build-essential \
    ghostscript \
    imagemagick ffmpeg \
    libmagic1 \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME path to use konlpy library
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64
ENV PATH $JAVA_HOME/bin:$PATH


RUN pip install --upgrade pip setuptools wheel
COPY input.pdf input.pdf
RUN  pdftoppm -png input.pdf output
# Install Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app
#COPY pyproject.toml poetry.lock /app/
COPY pyproject.toml poetry.lock /app/

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi

# Download spaCy models
#RUN pip install --no-cache-dir numpy==1.23.5 thinc==8.1.8
# Install a specific version of numpy that is compatible
#COPY samples samples
COPY quickstart.py .
#RUN python quickstart.py
RUN pip install jupyterlab pdfplumber

COPY . /app

# Run the Django application
#CMD ["tail", "-f", "/dev/null"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8501"]