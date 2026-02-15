
export interface User {
  id: string;
  name: string;
  handle: string;
  university: string;
  course: string;
  gradYear: number;
  avatar: string;
  isVerified: boolean;
  coverImage?: string;
  bio?: string;
  followers: number;
  following: number;
  skills?: string[];
  isMentor?: boolean;
  isMentee?: boolean;
  expertise?: string[];
  industry?: string;
}

export interface Post {
  id: string;
  authorId: string;
  author: User;
  content: string;
  image?: string;
  likes: number;
  comments: number;
  shares: number;
  timestamp: string;
  tags: string[];
}

export interface Notification {
  id: string;
  type: 'like' | 'comment' | 'follow' | 'mention' | 'university' | 'mentorship' | 'project';
  sender: User;
  timestamp: string;
  content: string;
  isRead: boolean;
}

export interface UniversityGroup {
  id: string;
  name: string;
  memberCount: number;
  category: 'Major' | 'Club' | 'Hobby' | 'Project';
  icon: string;
}

export interface UniEvent {
  id: string;
  title: string;
  date: string;
  time: string;
  location: string;
  description: string;
  university: string;
  type: 'academic' | 'social' | 'career';
  attendees: number;
}

export interface ProjectCall {
  id: string;
  creator: User;
  title: string;
  description: string;
  skillsNeeded: string[];
  outcomes: string;
  timestamp: string;
}

export interface MentorshipRequest {
  id: string;
  mentorId: string;
  menteeId: string;
  status: 'pending' | 'accepted' | 'declined';
  message: string;
}
