
FROM openjdk:11

RUN apt-get update && \
  apt-get install -y curl gnupg2 && \
  echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | tee /etc/apt/sources.list.d/sbt.list && \
  curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x99E82A75642AC823" | apt-key add && \
  apt-get update && \
  apt-get install -y sbt scala

WORKDIR /app

COPY build.sbt /app/
COPY project /app/project

RUN sbt update

COPY . /app

RUN sbt compile

EXPOSE 4040 7077 8080

CMD ["sbt", "run"]
