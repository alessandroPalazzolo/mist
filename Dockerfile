FROM debian:12

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1 

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    ca-certificates \
    sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
COPY . /opt/mist

##
# AFLGo
##
WORKDIR /opt/mist/AFLGo
RUN chmod +x build.sh && ./build.sh

##
# MIST
##
WORKDIR /opt/mist
RUN python3 -m pip install --no-cache-dir -e .

WORKDIR /workspace
CMD ["mist"]