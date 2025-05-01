FROM ubuntu:23.10

WORKDIR /app

COPY . /app

RUN chmod +x ./DuoBoloServer

EXPOSE 13333/udp

CMD ["timeout", "20m", "./DuoBoloServer"]
