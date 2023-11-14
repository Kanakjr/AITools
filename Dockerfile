# app/Dockerfile

FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip3 install -r requirements.txt

COPY app /app
WORKDIR /app

EXPOSE 8501
ENTRYPOINT ["python","-m","streamlit", "run", "ui.py", "--server.port=8503", "--server.address=0.0.0.0"]