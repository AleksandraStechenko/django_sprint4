from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView, DetailView
)


from .models import Post, Category, Comment, User
from .forms import PostForm, CommentForm, ProfileForm


PUBLICATIONS_PER_PAGE = 10


class CategoryListView(ListView):
    """Публикации в категории."""
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = PUBLICATIONS_PER_PAGE

    def get_queryset(self):
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'],
                                     is_published=True)
        return Post.objects.filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_count'] = Comment.objects.count()
        context['category'
                ] = get_object_or_404(Category,
                                      slug=self.kwargs['category_slug'],
                                      is_published=True)
        return context


class PostListView(ListView):
    """Лента записей."""
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PUBLICATIONS_PER_PAGE

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_count'] = Comment.objects.count()
        return context


class PostDetailView(DetailView):
    """Детали публикации."""
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post'] = post
        context['form'] = CommentForm()
        context['comments'] = post.comments.all()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_published and self.object.author != request.user:
            return render(request, 'pages/404.html', status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


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


class PostCreateView(LoginRequiredMixin,
                     PostMixin,
                     PostSuccessUrlMixin,
                     CreateView):
    """Добавление публикации."""
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        if 'image' in self.request.FILES:
            form.instance.image = self.request.FILES['image']
        self.object = form.save(commit=False)
        self.object.save()
        return super().form_valid(form)


class PostUpdateView(PostMixin,
                     LoginRequiredMixin,
                     UpdateView):
    """Редактирование публикации."""
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=instance.pk)
        self.kwargs['pk'] = kwargs['post_id']
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'pk': post_id})


class PostDeleteView(PostMixin,
                     LoginRequiredMixin,
                     PostSuccessUrlMixin,
                     DeleteView):
    """Удаление публикации."""
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            raise PermissionDenied
        self.kwargs['pk'] = kwargs['post_id']
        return super().dispatch(request, *args, **kwargs)


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


class CommentCreateView(CommentMixin,
                        LoginRequiredMixin,
                        CommentSuccessUrlMixin,
                        CreateView):
    """Добавление комментария."""

    def form_valid(self, form):
        form.instance.author = get_object_or_404(
            User, username=self.request.user)
        form.instance.post = get_object_or_404(
            Post, id=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin,
                        LoginRequiredMixin,
                        CommentDispatchMixin,
                        CommentSuccessUrlMixin,
                        UpdateView):
    """Редактирование комментария."""
    pass


class CommentDeleteView(CommentMixin,
                        LoginRequiredMixin,
                        CommentDispatchMixin,
                        DeleteView):
    """Удаление комментария."""
    success_url = reverse_lazy('blog:index')


class ProfileDetailView(DetailView):
    """Страница пользователя."""
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    paginate_by = PUBLICATIONS_PER_PAGE
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(
            User,
            username=self.kwargs['username'])

    def get_queryset(self):
        username = self.kwargs['username']
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            queryset = Post.objects.select_related(
                'category', 'location', 'author'
            ).filter(author=self.author).order_by('-pub_date')
        else:
            queryset = Post.objects.select_related(
                'category', 'location', 'author'
            ).filter(author=self.author,
                     is_published=True).order_by('-pub_date')
        queryset = queryset.annotate(comment_count=Count('comments'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.get_queryset()
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs.get('username'))
        post_images = [post.image for post in posts if post.image]
        context['image'] = post_images
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Изменение профиля."""
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_queryset(self):
        self.author = get_object_or_404(
            User, username=self.request.user
        )
        return User.objects.filter(username=self.request.user)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )
