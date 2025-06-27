FROM ghcr.io/epics-containers/ioc-generic-developer:2025.4.2b1

COPY records.db /ioc/records.db

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install pyepics (and epicscorelibs which bundles the shared libs)
RUN pip3 install pyepics epicscorelibs

COPY ./sim /usr/src/app/sim

COPY start.sh ./
RUN chmod +x start.sh

CMD ["./start.sh"]
