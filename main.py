from fastapi import FastAPI
from database import Base, engine
from routes import user_routes, item_routes
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(item_routes.router, prefix="/items", tags=["Items"])

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                await client.send_text(data)
    except WebSocketDisconnect:
        clients.remove(websocket)
