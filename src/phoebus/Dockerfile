# syntax=docker/dockerfile:1.4

FROM eclipse-temurin:latest

# Install dependencies for X11 forwarding
RUN apt-get update && apt-get install -y \
    curl \
    libgtk-3-0 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxext6 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Copy and extract tarball
RUN curl -L -o /opt/phoebus.tar.gz https://github.com/ControlSystemStudio/phoebus/releases/download/v5.0.0/phoebus-5.0.0.tar.gz \
    && tar -xzf /opt/phoebus.tar.gz -C /opt \
    && rm /opt/phoebus.tar.gz

CMD ["java", "-jar", "/opt/product-5.0.0/product-5.0.0.jar"]
