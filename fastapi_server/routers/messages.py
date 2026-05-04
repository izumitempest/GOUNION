from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, joinedload
from typing import List
import asyncio
from .. import crud, schemas, models, dependencies
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/conversations", tags=["messages"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast_to_conversation(self, message: dict, participant_ids: List[str]):
        for pid in participant_ids:
            if pid in self.active_connections:
                await self.active_connections[pid].send_json(message)

manager = ConnectionManager()

@router.get("/", response_model=List[schemas.Conversation])
def list_conversations(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_conversations(db, user_id=current_user.id)

@router.get("/{conversation_id}", response_model=schemas.Conversation)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    conv = db.query(models.Conversation).options(joinedload(models.Conversation.participants)).filter(models.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Not found")
    if current_user.id not in [p.id for p in conv.participants]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return conv

@router.post("/{conversation_id}/messages/", response_model=schemas.Message)
async def create_message(
    conversation_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    conv = db.query(models.Conversation).options(joinedload(models.Conversation.participants)).filter(models.Conversation.id == conversation_id).first()
    if not conv or current_user.id not in [p.id for p in conv.participants]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    db_message = crud.create_message(db, message=message, sender_id=current_user.id)
    full_message = db.query(models.Message).options(joinedload(models.Message.sender)).filter(models.Message.id == db_message.id).first()
    
    if full_message:
        msg_payload = {
            "type": "new_message",
            "message": {
                "id": full_message.id,
                "conversation_id": full_message.conversation_id,
                "content": full_message.content,
                "sender_id": full_message.sender_id,
                "created_at": full_message.created_at.isoformat(),
            }
        }
        asyncio.create_task(manager.broadcast_to_conversation(msg_payload, [p.id for p in conv.participants]))

    return full_message


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

