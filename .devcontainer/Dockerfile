FROM ubuntu:24.04


# Set non-interactive mode for APT to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install basic tools
RUN apt update && apt install -y \
    software-properties-common \
    curl \
    zip \
    unzip \
    tar \
    ca-certificates \
    git \
    wget \
    build-essential \
    vim \
    jq \
    && apt clean


# Download Anaconda and install it
RUN wget --no-check-certificate https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh -O /tmp/anaconda.sh && \
    bash /tmp/anaconda.sh -b -p /opt/conda && \
    rm /tmp/anaconda.sh

# Add Anaconda to the PATH
ENV PATH="/opt/conda/bin:$PATH"


# Unset non-interactive mode after installation
ENV DEBIAN_FRONTEND=

# Set default shell to bash
SHELL ["/bin/bash", "-c"]

CMD ["bash"]