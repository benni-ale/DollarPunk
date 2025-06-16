FROM bitnami/spark:3.4.1

USER root
RUN install_packages python3-pip
USER 1001

WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY .env ./
COPY *.py ./
RUN mkdir -p /app/data
VOLUME /app/data

ENV PYSPARK_SUBMIT_ARGS="--packages io.delta:delta-core_2.12:2.4.0 pyspark-shell"
CMD ["python3", "stock_news.py"] 