#!/bin/bash

# 打印环境变量（用于调试）
echo "Configuring environment variables..."
echo "API URL: ${VITE_API_URL}"
echo "WebSocket URL: ${VITE_API_WS}"
echo "App Name: ${VITE_APP_NAME}"
echo "API Version: ${VITE_API_VERSION}"

# 使用环境变量创建 config.js 文件
cat <<EOF > /app/dist/config.js
window.__ENV__ = {
  VITE_API_URL: "${VITE_API_URL}",
  VITE_API_WS: "${VITE_API_WS}",
  VITE_APP_NAME: "${VITE_APP_NAME}",
  VITE_API_VERSION: "${VITE_API_VERSION}"
};
EOF

# 打印生成的 config.js 文件内容（用于调试）
echo "Generated config.js:"
cat /app/dist/config.js

# 启动前端服务器（使用 serve 提供静态文件服务）
echo "Starting the server..."
npm run serve
