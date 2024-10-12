#!/bin/bash

# 镜像名称和版本
FRONTEND_IMAGE_NAME="registry.cn-hangzhou.aliyuncs.com/omini/frontend"
BACKEND_IMAGE_NAME="registry.cn-hangzhou.aliyuncs.com/omini/backend"
TAG="latest"

# 停止并移除当前运行的容器
docker-compose down

# 删除指定本地镜像的函数
remove_local_image() {
  IMAGE_NAME=$1
  echo "删除本地镜像: $IMAGE_NAME:$TAG"
  docker rmi $IMAGE_NAME:$TAG || true  # 如果镜像不存在，忽略错误
}

# 删除前端和后端镜像
remove_local_image $FRONTEND_IMAGE_NAME
remove_local_image $BACKEND_IMAGE_NAME

# 重新启动容器
docker-compose up -d

# 确认容器状态
docker-compose ps
