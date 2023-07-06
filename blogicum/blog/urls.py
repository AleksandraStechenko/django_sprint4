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
    path('posts/<int:id>/',
         PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/',
         CategoryListView.as_view(), name='category_posts'),
    path('posts/<int:post_id>/add_comment/',
         CommentCreateView.as_view(), name='add_comment'),
    path('posts/create/',
         PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/',
         PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/',
         PostDeleteView.as_view(), name='delete_post'),
    path('comment/<int:post_id>/create/',
         CommentCreateView.as_view(), name='create_comment'),
    path('comment/<int:post_id>/edit/',
         CommentUpdateView.as_view(), name='edit_comment'),
    path('comment/<int:post_id>/delete/',
         CommentDeleteView.as_view(), name='delete_comment'),
    path('profile/<slug:username>/',
         ProfileDetailView.as_view(), name='profile'),
    path('user/<slug:username>/',
         ProfileUpdateView.as_view(), name='edit_profile')
]
