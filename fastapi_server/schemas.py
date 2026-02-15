# schemas.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProfileBase(BaseModel):
    bio: Optional[str] = None
    university: Optional[str] = None
    profile_type: Optional[str] = "friend"
    course: Optional[str] = None
    graduation_year: Optional[int] = None
    cover_photo: Optional[str] = None
    relationship_status: Optional[str] = None
    hometown: Optional[str] = None
    # birth_date: Optional[date] = None # Keeping it simple for now to avoid parsing issues


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    profile_picture: Optional[str] = None


class Profile(ProfileBase):
    id: int
    user_id: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    email: str
    password: str


class User(UserBase):
    id: str
    is_active: bool
    profile: Optional[Profile] = None

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    user_id: str
    post_id: int
    created_at: datetime
    user: User

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    caption: Optional[str] = None
    image: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class Post(PostBase):
    id: int
    user_id: str
    image: Optional[str] = None
    created_at: datetime
    user: User
    comments: List[Comment] = []
    likes: List[User] = []
    likes_count: int = 0

    class Config:
        from_attributes = True


class FriendRequestBase(BaseModel):
    pass


class FriendRequestCreate(FriendRequestBase):
    receiver_id: str


class FriendRequest(FriendRequestBase):
    id: int
    sender_id: str
    receiver_id: str
    status: str
    created_at: datetime
    sender: User
    receiver: User

    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    pass


class Notification(NotificationBase):
    id: int
    user_id: str
    sender_id: str
    type: str
    post_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    sender: User

    class Config:
        from_attributes = True


class UserDeviceBase(BaseModel):
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    os_version: Optional[str] = None
    browser: Optional[str] = None
    ip_address: Optional[str] = None
    fcm_token: Optional[str] = None


class UserDeviceCreate(UserDeviceBase):
    pass


class UserDevice(UserDeviceBase):
    id: int
    user_id: str
    last_active: datetime

    class Config:
        from_attributes = True


class ActivityLogBase(BaseModel):
    action: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLog(ActivityLogBase):
    id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class LocationHistoryBase(BaseModel):
    latitude: float
    longitude: float
    city: Optional[str] = None
    country: Optional[str] = None


class LocationHistoryCreate(LocationHistoryBase):
    pass


class LocationHistory(LocationHistoryBase):
    id: int
    user_id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    privacy: str = "public"


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id: int
    creator_id: str
    cover_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GroupMemberBase(BaseModel):
    pass


class GroupMember(GroupMemberBase):
    id: int
    group_id: int
    user_id: str
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class GroupPost(BaseModel):
    id: int
    group_id: int
    user_id: str
    caption: Optional[str] = None
    image: Optional[str] = None
    created_at: datetime
    user: User

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    conversation_id: Optional[int] = None


class Message(MessageBase):
    id: int
    conversation_id: int
    sender_id: str
    created_at: datetime
    is_read: bool
    sender: User

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    name: Optional[str] = None


class ConversationCreate(ConversationBase):
    participant_ids: List[str]


class Conversation(ConversationBase):
    id: int
    created_at: datetime
    participants: List[User]
    messages: List[Message] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class StoryBase(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None


class StoryCreate(StoryBase):
    pass


class StoryView(BaseModel):
    id: int
    story_id: int
    user_id: str
    viewed_at: datetime

    class Config:
        from_attributes = True


class StoryLike(BaseModel):
    id: int
    story_id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class Story(StoryBase):
    id: int
    user_id: str
    created_at: datetime
    expires_at: datetime
    user: User
    views: List[StoryView] = []
    likes: List[StoryLike] = []

    class Config:
        from_attributes = True
