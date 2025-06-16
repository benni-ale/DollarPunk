FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY .env ./
COPY *.py ./
RUN mkdir -p /app/data
VOLUME /app/data
CMD ["python", "01.py"] 