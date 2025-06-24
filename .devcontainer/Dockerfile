FROM eclipse-temurin:latest

# Install python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
    
# Install VisualDCT
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxext6 \
    libxrandr2 \
    libgtk2.0-0 \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir /opt/visualDCT \
    && curl -L -o /opt/visualDCT.tar.gz https://github.com/epics-extensions/VisualDCT/releases/download/v2.8.3/VisualDCT-2.8.3-distribution.tar.gz \
    && tar -xzvf /opt/visualDCT.tar.gz -C /opt/visualDCT --strip-components=1 \
    && rm /opt/visualDCT.tar.gz
WORKDIR /opt/visualDCT
COPY assets/dbd.tar.gz ./share/dbd.tar.gz
RUN tar -xzf ./share/dbd.tar.gz -C ./share/ \
    && rm ./share/dbd.tar.gz

# Install Docker CLI and Compose V2
RUN apt-get update && apt-get install -y \
    docker.io \
    curl \
    && mkdir -p ~/.docker/cli-plugins \
    && curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose \
    && chmod +x ~/.docker/cli-plugins/docker-compose

# Install Python dependencies
# TODO: Review --break-system-packages.  Should be okay in a container, but may break as more packages are added.
COPY assets/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

WORKDIR /home