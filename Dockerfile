FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY demo_data ./demo_data
COPY imagens ./imagens
COPY styles ./styles
COPY scripts ./scripts
COPY src ./src

ENV PYTHONPATH=/app/src
ENV RCAP_DEMO=1

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
