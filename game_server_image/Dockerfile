FROM ubuntu

RUN apt-get update && apt-get install -y openssl ca-certificates

ENV CURLOPT_SSL_VERIFYPEER=0

WORKDIR /app

COPY . /app

RUN chmod +x ./DuoBoloServer

EXPOSE 13333/udp

CMD ["timeout", "20m", "./DuoBoloServer"]
