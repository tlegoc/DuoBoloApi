FROM ubuntu:23.10

WORKDIR /app

COPY . /app

RUN chmod +x ./DuoBoloEngine

EXPOSE 13333/udp

CMD ["timeout", "1h", "./DuoBoloEngine"]
