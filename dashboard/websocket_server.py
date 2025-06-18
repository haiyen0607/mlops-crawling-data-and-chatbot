from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

app = FastAPI()

# Cho phép kết nối từ mọi frontend (nên giới hạn lại trong môi trường production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Danh sách các client WebSocket đang kết nối
clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Giữ kết nối mở
    except:
        clients.remove(websocket)  # Nếu client ngắt kết nối

@app.get("/notify")
async def notify_clients():
    disconnected = []
    for client in clients:
        try:
            await client.send_text("data_updated")
        except:
            disconnected.append(client)
    for c in disconnected:
        clients.remove(c)
    return {"status": "ok", "clients_notified": len(clients)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# from fastapi import FastAPI, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# from typing import List
# import uvicorn
# import json

# app = FastAPI()

# # Cho phép kết nối từ mọi frontend (nên giới hạn lại trong môi trường production)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Danh sách các client WebSocket đang kết nối
# clients: List[WebSocket] = []

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     clients.append(websocket)
#     print(f"[WebSocket] Client connected: {websocket.client}")
#     try:
#         while True:
#             await websocket.receive_text()  # Giữ kết nối mở
#     except:
#         clients.remove(websocket)
#         print(f"[WebSocket] Client disconnected: {websocket.client}")

# @app.get("/notify")
# async def notify_clients():
#     data = {
#         "type": "notify",
#         "message": "Trend data updated."
#     }

#     disconnected = []
#     for client in clients:
#         try:
#             await client.send_text(json.dumps(data))
#         except:
#             disconnected.append(client)
#     for c in disconnected:
#         clients.remove(c)

#     print(f"[Notify] Đã gửi notify đến {len(clients)} client")
#     return {"status": "ok", "clients_notified": len(clients)}
    
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
