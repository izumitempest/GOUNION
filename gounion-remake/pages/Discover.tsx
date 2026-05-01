import React, { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import {
  useInfiniteQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { Heart, MessageCircle, Volume2, VolumeX } from "lucide-react";
import { api } from "../services/api";
import { Post } from "../types";
import { useAuthStore } from "../store";

const isVideoUrl = (url?: string) => {
  if (!url) return false;
  return /\.(mp4|webm|mov|m4v|avi|mkv|m3u8)(\?|$)/i.test(url);
};

export const Discover = () => {
  const queryClient = useQueryClient();
  const { user: currentUser } = useAuthStore();
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const [isMuted, setIsMuted] = React.useState(true);
  const videoRefs = useRef<Record<string, HTMLVideoElement | null>>({});

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, status } =
    useInfiniteQuery({
      queryKey: ["discover-reels"],
      queryFn: api.posts.getReels,
      initialPageParam: 0,
      getNextPageParam: (lastPage, allPages) =>
        lastPage.length > 0 ? allPages.length : undefined,
    });

  const likeMutation = useMutation({
    mutationFn: (postId: string) => api.posts.like(postId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["discover-reels"] });
      queryClient.invalidateQueries({ queryKey: ["profile-posts"] });
    },
  });

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1, rootMargin: "100px" },
    );

    if (loadMoreRef.current) observer.observe(loadMoreRef.current);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  useEffect(() => {
    const elements = Object.values(videoRefs.current).filter(
      (el): el is HTMLVideoElement => Boolean(el),
    );
    if (!elements.length) return;

    const playObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const video = entry.target as HTMLVideoElement;
          if (entry.isIntersecting && entry.intersectionRatio > 0.65) {
            void video.play().catch(() => {});
          } else {
            video.pause();
          }
        });
      },
      { threshold: [0.25, 0.65, 0.9] },
    );

    elements.forEach((video) => playObserver.observe(video));
    return () => playObserver.disconnect();
  }, [data]);

  const uniqueReels = Array.from(
    new Map((data?.pages.flat() || []).map((post: Post) => [post.id, post])).values(),
  );
  const reels = uniqueReels.filter(
    (post: Post) => isVideoUrl(post.imageUrl) && post.author.id !== currentUser?.id,
  );

  if (status === "pending") {
    return (
      <div className="h-[calc(100vh-8rem)] flex items-center justify-center text-white/60">
        Loading reels...
      </div>
    );
  }

  return (
    <div className="fixed inset-0 md:pl-64 lg:pr-80 bg-black overflow-hidden z-0">
      <div className="h-full overflow-y-auto snap-y snap-mandatory hide-scrollbar">
        {reels.length === 0 ? (
          <div className="h-full flex items-center justify-center text-white/60">
            No reels yet.
          </div>
        ) : (
          reels.map((reel) => (
            <section
              key={reel.id}
              className="snap-start h-full relative bg-black flex items-center justify-center"
            >
              <video
                ref={(el) => {
                  videoRefs.current[reel.id] = el;
                }}
                src={reel.imageUrl}
                className="w-full h-full object-cover md:object-contain bg-black"
                loop
                muted={isMuted}
                playsInline
                preload="metadata"
                onClick={(e) => {
                  const video = e.currentTarget;
                  if (video.paused) void video.play();
                  else video.pause();
                }}
              />

              <button
                onClick={() => setIsMuted((prev) => !prev)}
                className="absolute top-6 right-6 z-20 w-12 h-12 rounded-full bg-black/40 backdrop-blur-md border border-white/10 text-white flex items-center justify-center hover:bg-black/60 transition-all"
                aria-label={isMuted ? "Unmute video" : "Mute video"}
              >
                {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>

              <div className="absolute inset-x-0 bottom-0 pb-32 pt-20 px-6 bg-gradient-to-t from-black/80 via-black/20 to-transparent pointer-events-none">
                <div className="flex items-end justify-between gap-8 pointer-events-auto">
                  <div className="flex-1 min-w-0 mb-4">
                    <Link
                      to={`/profile/${reel.author.username}`}
                      className="inline-flex items-center gap-3 mb-4 group"
                    >
                      <div className="w-12 h-12 rounded-full border-2 border-white/20 overflow-hidden group-hover:border-white transition-colors">
                        <img 
                          src={reel.author.avatarUrl} 
                          alt={reel.author.username}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <span className="font-black text-white text-lg tracking-tight hover:underline">
                        @{reel.author.username}
                      </span>
                    </Link>
                    <p className="text-white/90 text-sm leading-relaxed line-clamp-3 max-w-md font-medium">
                      {reel.content || "New reel"}
                    </p>
                  </div>
                  
                  <div className="flex flex-col items-center gap-6 mb-4">
                    <button
                      onClick={() => likeMutation.mutate(reel.id)}
                      className="group flex flex-col items-center gap-1.5"
                    >
                      <div className="w-14 h-14 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center group-hover:bg-white/20 transition-all active:scale-90">
                        <Heart
                          className={`w-7 h-7 transition-colors ${reel.isLiked ? "fill-pink-500 text-pink-500" : "text-white"}`}
                        />
                      </div>
                      <span className="text-[11px] font-black text-white">{reel.likes}</span>
                    </button>
                    
                    <button className="group flex flex-col items-center gap-1.5">
                      <div className="w-14 h-14 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center group-hover:bg-white/20 transition-all">
                        <MessageCircle className="w-7 h-7 text-white" />
                      </div>
                      <span className="text-[11px] font-black text-white">{reel.comments}</span>
                    </button>
                  </div>
                </div>
              </div>
            </section>
          ))
        )}
        <div ref={loadMoreRef} className="h-8" />
      </div>
    </div>
  );
};
