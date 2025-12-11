from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet)
router.register(r'posts', views.PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name='api-register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('feed/', views.feed_view, name='api-feed'),
    path('explore/', views.explore_view, name='api-explore'),
    path('posts/<int:pk>/like/', views.like_post, name='api-like-post'),
    path('friend-request/send/<str:username>/', views.send_friend_request, name='api-send-friend-request'),
    path('friend-request/<int:pk>/accept/', views.accept_friend_request, name='api-accept-friend-request'),
]
