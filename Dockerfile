FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt pyproject.toml ./
COPY .streamlit ./.streamlit
COPY src ./src
COPY policy_terms.json test_cases.json ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install --no-cache-dir -e .

EXPOSE 8000 8501
