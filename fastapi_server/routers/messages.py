from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, joinedload, selectinload
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
        dead_connections = []
        for pid in participant_ids:
            if pid in self.active_connections:
                try:
                    await self.active_connections[pid].send_json(message)
                except Exception:
                    dead_connections.append(pid)
        for pid in dead_connections:
            self.disconnect(pid)

manager = ConnectionManager()

@router.get("/", response_model=List[schemas.Conversation])
async def list_conversations(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return await asyncio.to_thread(crud.get_conversations, db, user_id=current_user.id)

def _sync_fetch_conversation(db: Session, conversation_id: int) -> dict:
    c = db.query(models.Conversation).options(selectinload(models.Conversation.participants).joinedload(models.User.profile)).filter(models.Conversation.id == conversation_id).first()
    if not c: return None
    return {
        "id": c.id,
        "name": c.name,
        "created_at": c.created_at,
        "participants": [{
            "id": p.id,
            "username": p.username,
            "is_active": p.is_active,
            "role": p.role,
            "profile": p.profile
        } for p in c.participants]
    }

@router.get("/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    authorized = await asyncio.to_thread(crud.is_user_in_conversation, db, current_user.id, conversation_id)
    if not authorized:
        raise HTTPException(status_code=403, detail="Access denied.")

    conv = await asyncio.to_thread(_sync_fetch_conversation, db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conv

@router.get("/{conversation_id}/messages/", response_model=List[schemas.Message])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    authorized = await asyncio.to_thread(crud.is_user_in_conversation, db, current_user.id, conversation_id)
    if not authorized:
        raise HTTPException(status_code=403, detail="Access denied.")
    
    return await asyncio.to_thread(crud.get_messages, db, conversation_id=conversation_id, skip=skip, limit=limit)

def _sync_get_full_message(db: Session, message_id: int):
    m = db.query(models.Message).options(
            joinedload(models.Message.sender),
            joinedload(models.Message.conversation).selectinload(models.Conversation.participants)
        ).filter(models.Message.id == message_id).first()
    if not m: return None
    return {
        "id": m.id,
        "conversation_id": m.conversation_id,
        "sender_id": m.sender_id,
        "content": m.content,
        "image_url": m.image_url,
        "video_url": m.video_url,
        "created_at": m.created_at,
        "is_read": m.is_read,
        "sender": m.sender,
        "conversation": {
            "participants": [{"id": p.id} for p in m.conversation.participants]
        }
    }

@router.post("/messages/", response_model=schemas.Message)
async def send_message(
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not message.conversation_id and not message.recipient_id:
        raise HTTPException(status_code=400, detail="Target missing.")

    if message.conversation_id:
        authorized = await asyncio.to_thread(crud.is_user_in_conversation, db, current_user.id, message.conversation_id)
        if not authorized:
            raise HTTPException(status_code=403, detail="Forbidden.")

    db_message = await asyncio.to_thread(crud.create_message, db, message, current_user.id)
    
    full_message_data = await asyncio.to_thread(_sync_get_full_message, db, db_message["id"])

    if full_message_data:
        payload = {
            "type": "new_message",
            "message": {
                "id": full_message_data["id"],
                "conversation_id": full_message_data["conversation_id"],
                "content": full_message_data["content"],
                "sender_id": full_message_data["sender_id"],
                "created_at": full_message_data["created_at"].isoformat(),
            }
        }
        p_ids = [p["id"] for p in full_message_data["conversation"]["participants"]]
        asyncio.create_task(manager.broadcast_to_conversation(payload, p_ids))

    return full_message_data

@router.post("/{conversation_id}/messages/", response_model=schemas.Message)
async def create_message(
    conversation_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    authorized = await asyncio.to_thread(crud.is_user_in_conversation, db, current_user.id, conversation_id)
    if not authorized:
        raise HTTPException(status_code=403, detail="Forbidden.")
    
    db_message = await asyncio.to_thread(crud.create_message, db, message, current_user.id, conversation_id)
    
    full_message_data = await asyncio.to_thread(_sync_get_full_message, db, db_message["id"])
    
    if full_message_data:
        payload = {
            "type": "new_message",
            "message": {
                "id": full_message_data["id"],
                "conversation_id": full_message_data["conversation_id"],
                "content": full_message_data["content"],
                "sender_id": full_message_data["sender_id"],
                "created_at": full_message_data["created_at"].isoformat(),
            }
        }
        p_ids = [p["id"] for p in full_message_data["conversation"]["participants"]]
        asyncio.create_task(manager.broadcast_to_conversation(payload, p_ids))

    return full_message_data

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        manager.disconnect(user_id)
