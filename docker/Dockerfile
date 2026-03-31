FROM python:3.12-slim

# Install necessary packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc python3-dev curl vim \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY .. .

USER root

# Create log directory
RUN mkdir -p /app/logs
RUN mkdir -p /app/bin

# Create launch script
RUN cat > "/app/bin/launch.sh" <<'EOF'
#!/bin/bash
# copyright (c) 2026, Frankzhou <frankzhou007@163.com>
exec guicorn -c gunicorn.conf.py app:app >> /app/logs/guicorn.out 2>&1
EOF
RUN chmod +x "/app/bin/*.sh"
ENV PATH="/app/bin:${PATH}"

# Healthcheck
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s \
  CMD curl -fs http://localhost:5000/health || exit 1

EXPOSE 5000

# Run gunicorn
CMD ["launch.sh"]