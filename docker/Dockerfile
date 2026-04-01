FROM python:3.12-alpine

RUN apk update && \
    apk add --no-cache \
    bash \
    gcc \
    musl-dev \
    python3-dev \
    curl \
    vim \
    && rm -rf /var/cache/apk/*

# Configure aliases
RUN echo "alias ll='ls -lah'" >> /root/.bashrc && \
    echo "alias la='ls -A'" >> /root/.bashrc && \
    echo "alias l='ls -CF'" >> /root/.bashrc

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

# Create log, binary, source directory
RUN mkdir -p /app/logs
RUN mkdir -p /app/bin

# Copy source code
RUN mkdir -p /app/src
COPY .. /app/src

# Set environment variables
ENV PATH="/app/bin:${PATH}"
ENV PYTHONPATH="/app/src:/app"

# Create launch script
RUN cat > /app/bin/launch.sh <<'EOF'
#!/bin/bash
# copyright (c) 2026, Frankzhou <frankzhou007@163.com>
echo "Starting application with gunicorn..."
exec gunicorn -c /app/src/gunicorn.conf.py app:app >> /app/logs/gunicorn.out 2>&1
EOF
RUN chmod +x /app/bin/launch.sh

# Healthcheck
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s \
  CMD curl -fs http://localhost:5000/health || exit 1

USER root

EXPOSE 5000

# Run gunicorn
CMD ["launch.sh"]