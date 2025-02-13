from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Item, User
from schemas import ItemCreate, ItemResponse
from auth import decode_access_token

router = APIRouter()
websocket_clients = []

@router.websocket("/ws/items")
async def websocket_items(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)

@router.post("/items")
async def create_item(item: ItemCreate, db: Session = Depends(get_db), token: str = Depends(decode_access_token)):
    user = db.query(User).filter(User.username == token["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_item = Item(name=item.name, description=item.description, owner_id=user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # Notify all WebSocket clients asynchronously
    for client in websocket_clients:
        await client.send_text(f"New item added: {item.name}")

    return db_item

@router.get("/users/me/items", response_model=List[ItemResponse])
def get_user_items(token: str, db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    user = db.query(User).filter(User.username == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.items
