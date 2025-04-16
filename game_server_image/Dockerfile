# Use minimal base image
FROM debian:bullseye-slim

# Install required dependencies (you can add more here)
#RUN apt-get update && apt-get install -y \
#    libssl-dev \
#    ca-certificates \
#    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy your game server files
COPY . /app

# Expose game server port (adjust if needed)
EXPOSE 7777/udp

# Set the default command
CMD ["./DuoBoloServer"]
