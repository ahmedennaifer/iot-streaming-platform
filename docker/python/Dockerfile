FROM python:3.10.14

WORKDIR /app

RUN apt-get update && \
    apt-get install -y wget net-tools iputils-ping

COPY pyproject.toml /app/
COPY src /app/src

RUN pip install poetry && poetry install

ENV PYTHONPATH="${PYTHONPATH}:/app/src/main/generator"

RUN chmod +x /app/src/main/generator/producer/producer.py
RUN chmod +x /app/src/main/generator/producer/run_both.sh

EXPOSE 9092 2181

CMD ["bash", "/app/src/main/generator/producer/run_both.sh"]


