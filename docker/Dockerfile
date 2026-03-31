FROM python:3.12-alpine

RUN apk update && \
    apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    curl \
    vim \
    && rm -rf /var/cache/apk/*

# Configure aliases
RUN cat > /etc/profile.d/aliases.sh <<'EOF'
alias ll='ls -lh --color=auto'
alias la='ls -lAh --color=auto'
alias l='ls -CF --color=auto'
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias df='df -h'
alias du='du -h'
alias free='free -h'
alias cls='clear'
EOF

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

# Copy source code
COPY .. .

USER root

# Create log directory
RUN mkdir -p /app/logs
RUN mkdir -p /app/bin

# Create launch script
RUN cat > /app/bin/launch.sh <<'EOF'
#!/bin/sh
# copyright (c) 2026, Frankzhou <frankzhou007@163.com>
echo "Starting application with gunicorn..."
cd /app
exec gunicorn -c gunicorn.conf.py app:app >> /app/logs/guicorn.out 2>&1
EOF
RUN chmod +x /app/bin/launch.sh

ENV PATH="/app/bin:${PATH}"

# Healthcheck
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s \
  CMD curl -fs http://localhost:5000/health || exit 1

EXPOSE 5000

# Run gunicorn
ENTRYPOINT ["/app/bin/launch.sh"]