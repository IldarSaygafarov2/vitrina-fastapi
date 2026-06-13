from fastapi import WebSocket

# connection manager
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: dict[int, dict[int, WebSocket]] = {}

#     async def connect(self, websocket: WebSocket, agent_id: int, director_id: int):
#         await websocket.accept()

#         if agent_id not in self.active_connections:
#             self.active_connections[agent_id] = {}
#         self.active_connections[agent_id][director_id] = websocket

#     async def send_personal_message(self, message: str, client_id: str):
#         if client_id in self.active_connections:
#             await self.active_connections[client_id].send_text(message)
#         else:
#             raise ValueError("Client not connected")

#     async def disconnect(self, agent_id: int, director_id: int):
#         if (
#             agent_id in self.active_connections
#             and director_id in self.active_connections
#         ):
#             del self.active_connections[agent_id][director_id]
#             if not self.active_connections[agent_id]:
#                 del self.active_connections[agent_id]

#     async def broadcast(self, message: str, agent_id: int, director_id: int):
#         """
#         Broadcasts a message to all users in the room.
#         """
#         if agent_id in self.active_connections:
#             for user_id, connection in self.active_connections[agent_id].items():
#                 message_with_class = {
#                     "text": message,
#                     "is_self": user_id == director_id,
#                 }
#                 await connection.send_json(message_with_class)


class ConnectionManager:
    def __init__(self):
        # Maps a unique user/client ID to their active WebSocket connection
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
        else:
            raise ValueError("Client not connected")

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()
