# 使用 Node.js 18.20 版本的官方镜像，确保架构兼容性
FROM node:18.20

# 设置工作目录为 /app
WORKDIR /app

# 安装依赖
# 先复制 package.json 和 package-lock.json (如果存在)
COPY package*.json ./
RUN npm install --legacy-peer-deps
RUN npm install -g serve

# 复制所有前端代码到工作目录
COPY . .

# 清理 npm 缓存
RUN npm cache clean --force

# 构建生产环境的前端应用
RUN npm run build

# 复制启动脚本到容器中，并确保有正确的执行权限
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 暴露应用所需的端口
EXPOSE 3000

# 使用自定义的启动脚本启动应用
CMD ["/entrypoint.sh"]
