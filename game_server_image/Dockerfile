FROM ubuntu:23.10

RUN apt-get update && apt-get install -y netcat

WORKDIR /app

COPY . /app

RUN chmod +x ./DuoBoloEngine
RUN chmod +x ./launch.sh

EXPOSE 13333/udp

CMD ["./launch.sh"]
