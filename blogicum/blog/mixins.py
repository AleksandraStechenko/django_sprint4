from django.core.exceptions import PermissionDenied
from django.urls import reverse

from .forms import CommentForm
from .models import Comment, Post


class PostMixin:
    """Mixin для публикаций."""
    model = Post
    template_name = 'blog/create.html'


class PostSuccessUrlMixin:
    """
    Mixin для переадресации после создания или удаления поста.
    """

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentMixin:
    """Mixin для комментариев."""
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm


class CommentDispatchMixin:
    """Mixin для проверки доступа к редактированию и удалению комментария."""

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CommentSuccessUrlMixin:
    """
    Mixin для переадресации после создания или редактирования комментария.
    """

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'pk': post_id})