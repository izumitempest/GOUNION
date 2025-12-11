from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from social.models import Post, Profile, Comment, FriendRequest, Follow
from .serializers import UserSerializer, ProfileSerializer, PostSerializer, CommentSerializer, FriendRequestSerializer
from django.db.models import Q
from django.shortcuts import get_object_or_404

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, password=password, email=email)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    def get_queryset(self):
        return Profile.objects.select_related('user')

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Filter for feed if needed, currently returning all for simplicity or specific feed logic
        return Post.objects.all().order_by('-created_at')

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def feed_view(request):
    user = request.user
    friends = User.objects.filter(
        Q(sent_requests__receiver=user, sent_requests__status='accepted') |
        Q(received_requests__sender=user, received_requests__status='accepted')
    )
    following = User.objects.filter(followers__follower=user)
    feed_users = list(friends) + list(following) + [user]
    posts = Post.objects.filter(user__in=feed_users).distinct().order_by('-created_at')
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        return Response({'status': 'unliked'})
    else:
        post.likes.add(request.user)
        return Response({'status': 'liked'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    if request.user != to_user:
        FriendRequest.objects.get_or_create(sender=request.user, receiver=to_user, status='pending')
        return Response({'status': 'request sent'})
    return Response({'error': 'Cannot send request to self'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_friend_request(request, pk):
    friend_request = get_object_or_404(FriendRequest, pk=pk)
    if friend_request.receiver == request.user:
        friend_request.status = 'accepted'
        friend_request.save()
        return Response({'status': 'accepted'})
    return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def explore_view(request):
    users = User.objects.exclude(id=request.user.id)
    # We can use ProfileSerializer to return user profiles
    profiles = Profile.objects.filter(user__in=users)
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)
