#!/bin/bash
python -m spacy download ja_core_news_sm
export PORT=${PORT:-8000}
uvicorn main:app --host 0.0.0.0 --port $PORT 