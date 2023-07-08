from django.urls import path

from .views import (PostListView,
                    PostDetailView,
                    CategoryListView,
                    PostCreateView,
                    PostUpdateView,
                    PostDeleteView,
                    CommentCreateView,
                    CommentUpdateView,
                    CommentDeleteView,
                    ProfileDetailView,
                    ProfileUpdateView)

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='index'),
    path('category/<slug:category_slug>/',
         CategoryListView.as_view(), name='category_posts'),
    path('posts/<int:pk>/',
         PostDetailView.as_view(), name='post_detail'),
    path('posts/create/',
         PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/',
         PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/',
         PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/comment/create/',
         CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/comment/<int:pk>/update/',
         CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/comment/<int:pk>/delete/',
         CommentDeleteView.as_view(), name='delete_comment'),
    path('profile/<slug:username>/',
         ProfileDetailView.as_view(), name='profile'),
    path('user/<slug:username>/update',
         ProfileUpdateView.as_view(), name='edit_profile')
]
