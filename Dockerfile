FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create directory for Stockfish
WORKDIR /stockfish

# Download and install Stockfish
RUN wget https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_16.tar.gz \
    && tar xf sf_16.tar.gz \
    && cd Stockfish-sf_16/src \
    && make -j $(nproc) build ARCH=x86-64-modern \
    && mv stockfish /usr/local/bin/ \
    && cd / \
    && rm -rf /stockfish

# Set the working directory
WORKDIR /app

# Command to run Stockfish
CMD ["stockfish"] 