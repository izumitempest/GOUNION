/// <reference types="vite/client" />
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
});

// Add interceptor to include token
apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Helper to build full URLs for media
const getFullUrl = (url: string | null) => {
  if (!url) return null;
  if (url.startsWith('http')) return url;
  if (url.startsWith('blob:')) return url;
  const cleanUrl = url.startsWith('/') ? url : `/${url}`;
  return `${API_URL}${cleanUrl}`;
};

// Helper to transform user data
export const transformUser = (user: any) => {
  return {
    id: user.id,
    username: user.username,
    fullName: user.profile?.full_name || user.username,
    avatarUrl: getFullUrl(user.profile?.profile_picture) || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`,
    university: user.profile?.university || 'University Student',
    followers: 0,
    following: 0,
    bio: user.profile?.bio || '',
    coverUrl: getFullUrl(user.profile?.cover_photo) || '',
    isFollowing: false,
  };
};

const transformPost = (post: any) => {
  const userStr = sessionStorage.getItem('user_data');
  const user = userStr ? JSON.parse(userStr) : null;
  const currentUserId = user ? user.id : null;

  // Support both 'image' and 'video' fields from the backend
  const rawMedia = post.video || post.image;

  return {
    id: post.id.toString(),
    author: transformUser(post.user),
    content: post.caption || '',
    imageUrl: getFullUrl(rawMedia),   // kept as imageUrl for compatibility; MediaPlayer auto-detects type
    likes: post.likes_count || 0,
    comments: post.comments?.length || 0,
    timestamp: new Date(post.created_at).toLocaleDateString(),
    isLiked: post.likes?.some((l: any) => l.id === currentUserId) || false,
    groupId: post.group_id?.toString(),
  };
};

export const api = {
  auth: {
    login: async (credentials: any) => {
      const formData = new FormData();
      formData.append('username', credentials.email); // OAuth2 expects username
      formData.append('password', credentials.password);
      
      const res = await apiClient.post('/token', formData);
      const accessToken = res.data.access_token;
      sessionStorage.setItem('access_token', accessToken);
      
      const userRes = await apiClient.get('/users/me/');
      const transformedUser = transformUser(userRes.data);
      sessionStorage.setItem('user_data', JSON.stringify(transformedUser));
      sessionStorage.setItem('user_id', transformedUser.id);
      
      return { user: transformedUser, access_token: accessToken };
    },
    signup: async (data: any) => {
      const res = await apiClient.post('/users/', {
        username: data.username,
        email: data.email,
        password: data.password
      });
      
      // Auto-login after signup
      return api.auth.login({ email: data.email, password: data.password });
    },
    me: async () => {
      const res = await apiClient.get('/users/me/');
      return transformUser(res.data);
    },
    forgotPassword: async (email: string) => {
      const res = await apiClient.post('/auth/forgot-password', { email });
      return res.data;
    },
    resetPassword: async (token: string, new_password: string) => {
      const res = await apiClient.post('/auth/reset-password', { token, new_password });
      return res.data;
    },
  },
  posts: {
    getFeed: async ({ pageParam = 0 }: { pageParam?: number } = {}) => {
      const res = await apiClient.get(`/posts/?skip=${pageParam * 10}&limit=10`);
      return res.data.map(transformPost);
    },
    create: async (data: any) => {
      let mediaUrl = null;
      if (data.image) {
        const formData = new FormData();
        formData.append('file', data.image);
        const uploadRes = await apiClient.post('/upload/', formData);
        mediaUrl = uploadRes.data.url;
      }

      const isVideo = data.image?.type?.startsWith('video/');
      const res = await apiClient.post('/posts/', {
        caption: data.caption,
        image: isVideo ? null : mediaUrl,
        video: isVideo ? mediaUrl : null,
      });
      return transformPost(res.data);
    },
    like: async (id: string) => {
      const res = await apiClient.post(`/posts/${id}/like`);
      return { success: true, likes_count: res.data.likes_count };
    },
    getComments: async (id: string) => {
      const res = await apiClient.get(`/posts/${id}/comments`);
      return res.data;
    },
    createComment: async (id: string, content: string) => {
      const res = await apiClient.post(`/posts/${id}/comments/`, { content });
      return res.data;
    }
  },
  profiles: {
    get: async (username: string) => {
      const res = await apiClient.get(`/profiles/${username}`);
      const d = res.data;
      return {
        id: d.user_id,
        username: d.username || username,
        fullName: d.full_name || d.username || username,
        avatarUrl: getFullUrl(d.profile_picture) || `https://api.dicebear.com/7.x/avataaars/svg?seed=${username}`,
        university: d.university || 'University Student',
        followers: d.followers_count ?? 0,
        following: d.following_count ?? 0,
        bio: d.bio || '',
        coverUrl: getFullUrl(d.cover_photo) || '',
        isFollowing: d.is_following ?? false,
        course: d.course || '',
        hometown: d.hometown || '',
      };
    },
    getPosts: async (username: string) => {
      // First get the user's ID from their profile
      const profileRes = await apiClient.get(`/profiles/${username}`);
      const userId = profileRes.data.user_id;
      // Use dedicated server-side endpoint for efficiency
      const res = await apiClient.get(`/users/${userId}/posts?limit=50`);
      return res.data.map(transformPost);
    },
    update: async (data: any) => {
      let profile_picture = data.profile_picture;
      
      if (data.avatar) {
        const formData = new FormData();
        formData.append('file', data.avatar);
        const uploadRes = await apiClient.post('/upload/', formData);
        profile_picture = uploadRes.data.url;
      }

      const res = await apiClient.put('/profiles/me', {
        full_name: data.fullName,
        bio: data.bio,
        university: data.university,
        profile_picture: profile_picture
      });
      
      // Profiles/me returns the profile object, but we need the user object for transformUser
      // Let's refetch me or just handle it. 
      // Actually, transformUser expects user structure. 
      const userRes = await apiClient.get('/users/me/');
      return transformUser(userRes.data);
    },
    follow: async (userId: string) => {
      const res = await apiClient.post(`/users/${userId}/follow`);
      return res.data;
    },
    unfollow: async (userId: string) => {
      const res = await apiClient.post(`/users/${userId}/unfollow`);
      return res.data;
    },
    getFollowing: async (userId: string) => {
      const res = await apiClient.get(`/users/${userId}/following`);
      return res.data.map(transformUser);
    },
    getFollowers: async (userId: string) => {
      const res = await apiClient.get(`/users/${userId}/followers`);
      return res.data.map(transformUser);
    },
    getSuggestions: async () => {
      const res = await apiClient.get('/search/users?q=');
      return res.data.map(transformUser).filter((u: any) => u.id !== sessionStorage.getItem('user_id'));
    }
  },
  groups: {
    getAll: async () => {
      const res = await apiClient.get('/groups/');
      return res.data.map((g: any) => ({
        id: g.id.toString(),
        name: g.name,
        description: g.description,
        memberCount: 0, // Backend could provide this or we calculate
        imageUrl: getFullUrl(g.cover_image) || `https://api.dicebear.com/7.x/identicon/svg?seed=${g.name}`,
        isJoined: false,
        privacy: g.privacy
      }));
    },
    getById: async (id: string) => {
      const res = await apiClient.get(`/groups/${id}`);
      const g = res.data;
      return {
        id: g.id.toString(),
        name: g.name,
        description: g.description,
        memberCount: 0,
        imageUrl: getFullUrl(g.cover_image) || `https://api.dicebear.com/7.x/identicon/svg?seed=${g.name}`,
        isJoined: false,
        privacy: g.privacy,
        creatorId: g.creator_id
      };
    },
    getMembers: async (id: string) => {
      const res = await apiClient.get(`/groups/${id}/members/`);
      return res.data;
    },
    join: async (id: string) => {
      const res = await apiClient.post(`/groups/${id}/join`);
      return res.data; // { status: 'joined' | 'pending', message: string }
    },
    getRequests: async (id: string) => {
      const res = await apiClient.get(`/groups/${id}/requests/`);
      return res.data;
    },
    approveRequest: async (requestId: number, status: 'accepted' | 'rejected') => {
      const res = await apiClient.post(`/groups/requests/${requestId}/approve?status=${status}`);
      return res.data;
    },
    create: async (data: any) => {
      let cover_image = null;
      if (data.image) {
        const formData = new FormData();
        formData.append('file', data.image);
        const uploadRes = await apiClient.post('/upload/', formData);
        cover_image = uploadRes.data.url;
      }
      const res = await apiClient.post('/groups/', {
        name: data.name,
        description: data.description,
        privacy: data.privacy,
        cover_image: cover_image
      });
      return res.data;
    },
    getPosts: async (id: string) => {
      const res = await apiClient.get(`/groups/${id}/posts/`);
      return res.data.map(transformPost);
    },
    createPost: async (id: string, data: any) => {
      let imageUrl = null;
      if (data.image) {
        const formData = new FormData();
        formData.append('file', data.image);
        const uploadRes = await apiClient.post('/upload/', formData);
        imageUrl = uploadRes.data.url;
      }
      const res = await apiClient.post(`/groups/${id}/posts/`, {
        caption: data.caption,
        image: imageUrl
      });
      return transformPost(res.data);
    }
  },
  search: {
    users: async (query: string) => {
      const res = await apiClient.get(`/search/users?q=${encodeURIComponent(query)}`);
      return res.data.map(transformUser);
    }
  },
  friends: {
    getAll: async () => {
      const res = await apiClient.get('/friends/');
      return res.data.map(transformUser);
    },
    sendRequest: async (userId: string) => {
      const res = await apiClient.post(`/friend-request/${userId}`);
      return res.data;
    }
  },
  chats: {
    getAll: async () => {
      const res = await apiClient.get('/conversations/');
      const currentUserId = sessionStorage.getItem('user_id');
      return res.data.map((c: any) => ({
        id: c.id.toString(),
        partner: transformUser(c.participants.find((p: any) => p.id !== currentUserId) || c.participants[0]),
        lastMessage: c.messages?.[c.messages.length - 1]?.content || 'No messages yet',
        timestamp: c.messages?.[c.messages.length - 1] ? new Date(c.messages[c.messages.length - 1].created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
        unreadCount: 0,
      }));
    },
    getMessages: async (conversationId: string) => {
      const res = await apiClient.get(`/conversations/${conversationId}/messages/`);
      return res.data.map((m: any) => ({
        id: m.id.toString(),
        content: m.content,
        senderId: m.sender_id,
        timestamp: new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isRead: m.is_read
      }));
    },
    sendMessage: async (conversationId: string, content: string) => {
      const res = await apiClient.post(`/conversations/${conversationId}/messages/`, { content });
      return res.data;
    },
    createConversation: async (participantIds: string[], name?: string) => {
      const res = await apiClient.post('/conversations/', { participant_ids: participantIds, name });
      return res.data;
    }
  },
  notifications: {
    getAll: async () => {
      const res = await apiClient.get('/notifications/');
      return res.data.map((n: any) => ({
        id: n.id.toString(),
        type: n.type,
        actor: transformUser(n.sender),
        message: `${n.sender.username} ${n.type}ed your post`,
        timestamp: new Date(n.created_at).toLocaleDateString(),
        read: n.is_read
      }));
    }
  },
  stories: {
    getFeed: async () => {
      const res = await apiClient.get('/stories/feed');
      return res.data.map((s: any) => ({
        id: s.id.toString(),
        user: transformUser(s.user),
        content: s.content,
        imageUrl: getFullUrl(s.image_url),
        timestamp: new Date(s.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        likesCount: s.likes?.length || 0,
        viewsCount: s.views?.length || 0,
        isLiked: s.likes?.some((l: any) => l.user_id === sessionStorage.getItem('user_id')),
      }));
    },
    create: async (data: any) => {
      let imageUrl = null;
      if (data.image) {
        const formData = new FormData();
        formData.append('file', data.image);
        const uploadRes = await apiClient.post('/upload/', formData);
        imageUrl = uploadRes.data.url;
      }
      const res = await apiClient.post('/stories/', {
        content: data.content,
        image_url: imageUrl
      });
      return res.data;
    },
    view: async (id: string) => {
      await apiClient.post(`/stories/${id}/view`);
    },
    like: async (id: string) => {
      const res = await apiClient.post(`/stories/${id}/like`);
      return res.data;
    }
  }
};
