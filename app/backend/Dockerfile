# 使用官方的 Python 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装基本工具和 Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    ca-certificates \
    unzip \
    gcc \
    python3-dev \
 && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
 && apt-get update \
 && apt-get install -y google-chrome-stable \
 && wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip \
 && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
 && rm -rf /var/lib/apt/lists/* chromedriver_linux64.zip

# 复制 Python 依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 复制应用代码到容器中
COPY . /app


# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露应用运行的端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
