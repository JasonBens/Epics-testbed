FROM ghcr.io/epics-containers/ioc-generic-developer:2025.4.2b1

COPY records.db /ioc/records.db
COPY st.cmd /ioc/st.cmd

WORKDIR /ioc

RUN chmod +x st.cmd

CMD ["./st.cmd"]
