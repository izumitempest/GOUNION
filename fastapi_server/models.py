from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table, Date, Float, JSON
from sqlalchemy.orm import relationship
from .database import Base
import datetime

# Association tables for Many-to-Many relationships
post_likes = Table('post_likes', Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('post_id', Integer, ForeignKey('posts.id'))
)

post_dislikes = Table('post_dislikes', Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('post_id', Integer, ForeignKey('posts.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # UUID from Supabase Auth
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    # hashed_password removed - handled by Supabase Auth
    is_active = Column(Boolean, default=True)

    profile = relationship("Profile", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user", foreign_keys="[Notification.user_id]")
    
    # Data Collection Relationships
    devices = relationship("UserDevice", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    location_history = relationship("LocationHistory", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    bio = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True) # URL to image
    university = Column(String, nullable=True)
    profile_type = Column(String, default="friend") # 'friend' or 'follow'
    
    # Extended Profile Info
    cover_photo = Column(String, nullable=True)
    course = Column(String, nullable=True) # e.g. Computer Science
    graduation_year = Column(Integer, nullable=True)
    relationship_status = Column(String, nullable=True) # Single, Taken, etc.
    hometown = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="profile")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    image = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    
    likes = relationship("User", secondary=post_likes, backref="liked_posts")
    dislikes = relationship("User", secondary=post_dislikes, backref="disliked_posts")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("users.id"))
    receiver_id = Column(String, ForeignKey("users.id"))
    status = Column(String, default="pending") # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(String, ForeignKey("users.id"))
    following_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id")) # Receiver
    sender_id = Column(String, ForeignKey("users.id")) # Actor
    type = Column(String) # 'like', 'comment', 'friend_request', 'follow'
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    sender = relationship("User", foreign_keys=[sender_id])

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    cover_image = Column(String, nullable=True)
    privacy = Column(String, default="public") # public, private, secret
    creator_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    creator = relationship("User")
    members = relationship("GroupMember", back_populates="group")
    posts = relationship("GroupPost", back_populates="group")

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(String, ForeignKey("users.id"))
    role = Column(String, default="member") # admin, moderator, member
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)

    group = relationship("Group", back_populates="members")
    user = relationship("User")

class GroupPost(Base):
    __tablename__ = "group_posts"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(String, ForeignKey("users.id"))
    caption = Column(String, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    group = relationship("Group", back_populates="posts")
    user = relationship("User")

class UserDevice(Base):
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    device_name = Column(String, nullable=True) # e.g. iPhone 13
    device_type = Column(String, nullable=True) # Mobile, Desktop
    os_version = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    fcm_token = Column(String, nullable=True) # For Push Notifications
    last_active = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="devices")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    action = Column(String) # login, post_create, etc.
    details = Column(JSON, nullable=True) # Extra data
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="activity_logs")

class LocationHistory(Base):
    __tablename__ = "location_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="location_history")

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    query = Column(String)
    clicked_result_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="search_history")
