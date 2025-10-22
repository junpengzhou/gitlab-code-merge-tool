FROM python:3.9-slim

# 安装必要的系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc python3-dev curl vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .. .

# 创建flaskuser用户增强安全性
RUN useradd -m flaskuser && chown -R flaskuser:flaskuser /app
RUN mkdir -p /app/logs && chown -R flaskuser:flaskuser /app/logs
USER flaskuser

# 健康检查
HEALTHCHECK --interval=60s --timeout=3s --start-period=40s \
  CMD curl -fs http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]