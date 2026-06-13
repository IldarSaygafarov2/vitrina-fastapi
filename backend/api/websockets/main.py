from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import manager

router = APIRouter(prefix="/ws")


# @router.websocket("/{agent_id}/{user_id}")
# async def websocket_endpoint(websocket: WebSocket, agent_id: int, director_id: int):
#     await manager.connect(websocket, agent_id, director_id)
#     await manager.broadcast(
#         f"(ID: {director_id}) has joined the chat.", agent_id, director_id
#     )

#     print("WEBSOCKET DATA: ", agent_id, director_id)

#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.broadcast(
#                 f"(ID: {director_id}): {data}", agent_id, director_id
#             )
#     except WebSocketDisconnect:
#         manager.disconnect(agent_id, director_id)
#         await manager.broadcast(
#             f"(ID: {director_id}) has left the chat.", agent_id, director_id
#         )


# @router.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     await manager.connect(client_id, websocket)
#     try:
#         while True:
#             # Keep the connection alive by listening for client data
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         manager.disconnect(client_id)
