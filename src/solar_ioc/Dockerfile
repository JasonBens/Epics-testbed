FROM ghcr.io/epics-containers/ioc-generic-developer:2025.4.2b1

COPY records.db /ioc/records.db

COPY start.sh /ioc/start.sh
RUN chmod +x /ioc/start.sh

CMD ["/ioc/start.sh"]