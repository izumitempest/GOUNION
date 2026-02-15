
import { User, Post, UniversityGroup, Notification, UniEvent, ProjectCall } from './types';

export const CURRENT_USER: User = {
  id: 'me',
  name: 'Alex Rivera',
  handle: '@arivera_cs',
  university: 'Stanford University',
  course: 'Computer Science & AI',
  gradYear: 2025,
  avatar: 'https://picsum.photos/seed/arivera/150/150',
  isVerified: true,
  bio: 'Building the future of academic networking. Junior @ Stanford. Passionate about LLMs and distributed systems.',
  followers: 1240,
  following: 890,
  skills: ['TypeScript', 'React', 'Python', 'LLMs', 'UI Design'],
  isMentor: true,
  isMentee: false,
  expertise: ['Software Architecture', 'Career Guidance'],
  industry: 'Technology',
};

export const MOCK_USERS: User[] = [
  {
    id: 'u1',
    name: 'Sarah Chen',
    handle: '@schen_design',
    university: 'Stanford University',
    course: 'Product Design',
    gradYear: 2024,
    avatar: 'https://picsum.photos/seed/sarah/150/150',
    isVerified: true,
    followers: 2100,
    following: 400,
    skills: ['Figma', 'UI/UX', 'Prototyping'],
    isMentor: true,
    expertise: ['Portfolio Review', 'Design Systems'],
    industry: 'Design',
  },
  {
    id: 'u2',
    name: 'Marcus Thorne',
    handle: '@mthorne_law',
    university: 'Harvard University',
    course: 'Juris Doctor',
    gradYear: 2026,
    avatar: 'https://picsum.photos/seed/marcus/150/150',
    isVerified: false,
    followers: 850,
    following: 320,
    skills: ['Public Speaking', 'Legal Writing', 'Research'],
    isMentor: false,
    isMentee: true,
  },
];

export const INITIAL_POSTS: Post[] = [
  {
    id: 'p1',
    authorId: 'u1',
    author: MOCK_USERS[0],
    content: 'Just finished the final prototype for my thesis project! Using mixed reality to help visual learners understand complex geometry. Would love some feedback from my peers in the CS department! 📐✨',
    image: 'https://picsum.photos/seed/thesis/800/450',
    likes: 342,
    comments: 24,
    shares: 12,
    timestamp: '2h ago',
    tags: ['Design', 'Stanford2024', 'MixedReality'],
  },
  {
    id: 'p2',
    authorId: 'u2',
    author: MOCK_USERS[1],
    content: 'The library is surprisingly quiet tonight. Grinding for the mock trial competition next week. Any other law students currently living off caffeine? ☕️⚖️',
    likes: 89,
    comments: 15,
    shares: 2,
    timestamp: '5h ago',
    tags: ['LawSchool', 'Harvard', 'Grind'],
  }
];

export const UNIVERSITY_GROUPS: UniversityGroup[] = [
  { id: 'g1', name: 'Stanford CS Masters', memberCount: 450, category: 'Major', icon: '💻' },
  { id: 'g2', name: 'AI Research Lab', memberCount: 120, category: 'Project', icon: '🤖' },
  { id: 'g3', name: 'Stanford Hiking Club', memberCount: 890, category: 'Hobby', icon: '🥾' },
  { id: 'g4', name: 'Silicon Valley Founders', memberCount: 2100, category: 'Club', icon: '🚀' },
];

export const MOCK_NOTIFICATIONS: Notification[] = [
  {
    id: 'n1',
    type: 'like',
    sender: MOCK_USERS[0],
    content: 'liked your post about "Distributed Systems Research"',
    timestamp: '5m ago',
    isRead: false,
  },
  {
    id: 'n2',
    type: 'university',
    sender: MOCK_USERS[1],
    content: 'joined the Stanford CS Masters group',
    timestamp: '1h ago',
    isRead: true,
  },
];

export const MOCK_EVENTS: UniEvent[] = [
  {
    id: 'e1',
    title: 'Silicon Valley Founders Mixer',
    date: 'Oct 15, 2024',
    time: '6:00 PM',
    location: 'Stanford Student Union',
    description: 'Join us for an evening of networking with founders and venture capitalists from across the bay.',
    university: 'Stanford University',
    type: 'career',
    attendees: 124,
  },
  {
    id: 'e2',
    title: 'Fall Welcome Social',
    date: 'Oct 20, 2024',
    time: '8:00 PM',
    location: 'White Plaza',
    description: 'Meet fellow students and enjoy live music and refreshments as we kick off the fall quarter.',
    university: 'Stanford University',
    type: 'social',
    attendees: 450,
  },
];

export const MOCK_PROJECT_CALLS: ProjectCall[] = [
  {
    id: 'pc1',
    creator: CURRENT_USER,
    title: 'Decentralized Academic Journal',
    description: 'Looking for a UI designer and a backend developer to build a blockchain-based platform for peer-reviewed research.',
    skillsNeeded: ['React', 'Solidity', 'UI Design'],
    outcomes: 'Prototype for the Stanford Research Fair.',
    timestamp: '1d ago',
  },
  {
    id: 'pc2',
    creator: MOCK_USERS[0],
    title: 'AR Campus Tour App',
    description: 'Building an AR app that highlights historical landmarks around Stanford campus.',
    skillsNeeded: ['Swift', 'Unity', 'History Research'],
    outcomes: 'Official launch on the App Store.',
    timestamp: '3h ago',
  },
];
