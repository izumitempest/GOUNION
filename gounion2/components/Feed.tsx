
import React from 'react';
import { Heart, MessageCircle, Share2, MoreHorizontal, Plus, Send } from 'lucide-react';
import { Post } from '../types';
import { MOCK_USERS } from '../constants';

interface FeedProps { posts: Post[]; }

const Feed: React.FC<FeedProps> = ({ posts }) => {
  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      {/* Stories / Circles Bar */}
      <div className="flex gap-4 overflow-x-auto pb-6 scrollbar-hide mb-8 border-b border-white/5">
        <div className="flex flex-col items-center gap-2 shrink-0 cursor-pointer">
          <div className="w-16 h-16 rounded-full border-2 border-dashed border-zinc-700 flex items-center justify-center text-zinc-500 hover:border-[#c4ff0e] hover:text-[#c4ff0e] transition-all">
            <Plus className="w-6 h-6" />
          </div>
          <span className="text-[10px] font-bold text-zinc-500">Your Story</span>
        </div>
        {MOCK_USERS.map(user => (
          <div key={user.id} className="flex flex-col items-center gap-2 shrink-0 cursor-pointer group">
            <div className="w-16 h-16 rounded-full story-ring p-[2px] shadow-[0_0_15px_rgba(196,255,14,0.1)] group-hover:shadow-[0_0_20px_rgba(196,255,14,0.3)] transition-all">
              <div className="w-full h-full rounded-full border-2 border-black overflow-hidden">
                <img src={user.avatar} className="w-full h-full object-cover" />
              </div>
            </div>
            <span className="text-[10px] font-bold text-zinc-400 group-hover:text-white transition-colors">{user.name.split(' ')[0]}</span>
          </div>
        ))}
      </div>

      {/* Feed Area */}
      <div className="space-y-6">
        {posts.map((post) => (
          <article key={post.id} className="glass-card rounded-[32px] overflow-hidden transition-all hover:translate-y-[-2px] hover:shadow-[0_20px_40px_rgba(0,0,0,0.4)]">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full border-2 border-[#c4ff0e]/30 overflow-hidden">
                    <img src={post.author.avatar} className="w-full h-full object-cover" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                        <h3 className="text-sm font-bold text-white">{post.author.name}</h3>
                        {post.author.isVerified && <div className="w-3 h-3 bg-purple-500 rounded-full flex items-center justify-center text-[6px] font-bold">✓</div>}
                    </div>
                    <p className="text-[10px] font-medium text-zinc-500">{post.author.university} • {post.timestamp}</p>
                  </div>
                </div>
                <button className="p-2 text-zinc-600 hover:text-white transition-colors"><MoreHorizontal className="w-5 h-5"/></button>
              </div>

              {/* Content */}
              <div className="text-white text-sm leading-relaxed mb-4">
                {post.content}
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-6">
                {post.tags.map(tag => (
                  <span key={tag} className="text-[10px] font-bold text-[#c4ff0e] px-2 py-1 bg-[#c4ff0e]/10 rounded-full">#{tag}</span>
                ))}
              </div>

              {/* Media */}
              {post.image && (
                <div className="mb-6 rounded-3xl overflow-hidden border border-white/5 aspect-video bg-zinc-900 flex items-center justify-center">
                  <img src={post.image} className="w-full h-full object-cover" loading="lazy" />
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <div className="flex items-center gap-6">
                  <button className="flex items-center gap-2 text-zinc-400 hover:text-[#c4ff0e] transition-colors group">
                    <div className="p-2 rounded-full group-hover:bg-[#c4ff0e]/10">
                        <Heart className="w-5 h-5" />
                    </div>
                    <span className="text-xs font-bold">{post.likes}</span>
                  </button>
                  <button className="flex items-center gap-2 text-zinc-400 hover:text-purple-400 transition-colors group">
                    <div className="p-2 rounded-full group-hover:bg-purple-400/10">
                        <MessageCircle className="w-5 h-5" />
                    </div>
                    <span className="text-xs font-bold">{post.comments}</span>
                  </button>
                  <button className="p-2 text-zinc-400 hover:text-white transition-colors group">
                    <div className="p-2 rounded-full group-hover:bg-white/5">
                        <Send className="w-5 h-5" />
                    </div>
                  </button>
                </div>
                <button className="p-2 text-zinc-400 hover:text-white transition-colors">
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

export default Feed;
