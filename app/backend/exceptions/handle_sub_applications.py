from fastapi import FastAPI, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from utils.WebSocketManager import ConnectionManager
from utils.logging_config import LogManager

logger = LogManager.get_logger()
# 在这里创建一个ConnectionManager的实例
manager = ConnectionManager()
# 将 manager 通过依赖注入传递给其他路由
def get_connection_manager():
    return manager
def handle_sub_applications(app: FastAPI):

    # WebSocket 端点
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket, manager: ConnectionManager = Depends(get_connection_manager)):
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.broadcast(f"Message: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast("A client disconnected.")