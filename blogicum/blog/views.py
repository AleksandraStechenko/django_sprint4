from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView, TemplateView, DetailView
)


from .models import Post, Category, Comment, User
from .forms import PostForm, CommentForm, ProfileForm


PUBLICATIONS_PER_PAGE = 10


class CategoryListView(ListView):
    """Публикации в категории."""
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
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_count'] = Comment.objects.count()
        context[
            'category'
            ] = get_object_or_404(Category,
                                  slug=self.kwargs['category_slug'],
                                  is_published=True)
        return context


class PostListView(ListView):
    """Лента записей."""
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    ordering = 'id'
    paginate_by = PUBLICATIONS_PER_PAGE

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_count'] = Comment.objects.count()
        return context


class PostDetailView(TemplateView):
    """Детали публикации."""
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post,
                                 id=kwargs['id'],
                                 is_published=True,
                                 pub_date__lte=timezone.now(),
                                 category__is_published=True)
        context['post'] = post
        context['form'] = CommentForm()
        return context


class PostMixin:
    """Mixin для публикаций."""
    model = Post
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    """Добавление публикации."""
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.image = self.request.FILES['image']
        self.object = form.save(commit=False)
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(PostMixin,
                     LoginRequiredMixin,
                     UpdateView):
    """Редактирование публикации."""
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)    

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['id']})


class PostDeleteView(PostMixin,
                     LoginRequiredMixin,
                     DeleteView):
    """Удаление публикации."""
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    success_url = reverse_lazy('blog:index')


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Добавление комментария."""

    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'
    queryset = Comment.objects.select_related('author').filter(
        is_published=True)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'id': post_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        context['comment'] = comment
        return context

    def form_valid(self, form):
        form.instance.author = get_object_or_404(User, username=self.request.user)
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование комментария."""
    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'
    queryset = Comment.objects.select_related('author').filter(
        is_published=True)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'id': post_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        context['comment'] = comment
        return context

    def get_object(self):
        queryset = self.queryset.filter(pk=self.kwargs['comment_id'])
        return super().get_object(queryset=queryset)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'
    queryset = Comment.objects.select_related('author').filter(
        is_published=True)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'id': post_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        context['comment'] = comment
        return context


class ProfileDetailView(DetailView):
    """Страница пользователя."""
    model = Post
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    fields = '__all__'
    ordering = 'id'
    paginate_by = PUBLICATIONS_PER_PAGE
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return User.objects.get(username=self.kwargs['username'])

    def get_user_posts(self):
        return self.object.post_set.all()

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs.get('username'))
        instance = author.posts.filter(
            author__username__exact=self.kwargs.get('username')
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_object()
        posts = Post.objects.filter(author=author).order_by('-pub_date')
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['profile'] = get_object_or_404(
            User, username=self.kwargs.get('username')
            )
        context['comment_count'] = Comment.objects.count()
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
            kwargs={'username': self.request.user}
        )
