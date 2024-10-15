FROM python:3.10.14

WORKDIR /app

RUN apt-get update && \
    apt-get install -y wget net-tools iputils-ping

COPY pyproject.toml  /app/

RUN pip install poetry && poetry install

COPY kafka /app/kafka  


RUN chmod +x /app/kafka/consumer.py
RUN chmod +x /app/kafka/producer.py
RUN chmod +x /app/kafka/run_both.sh

EXPOSE 9092 2181

CMD ["bash", "/app/kafka/run_both.sh"]
