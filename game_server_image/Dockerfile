# Use minimal base image
#FROM debian:bookworm-slim

FROM ubuntu:23.10

# Create app directory
WORKDIR /app

# Copy your game server files
COPY . /app

RUN chmod +x ./DuoBoloEngine

# Expose game server port (adjust if needed)
EXPOSE 13333/udp

# Set the default command
CMD ["./DuoBoloEngine"]
