from django.contrib import admin


from .models import Category, Comment, Location, Post


admin.site.empty_value_display = 'Не задано'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'image',
        'pub_date',
        'author',
        'location',
        'category',
    )
    list_editable = (
        'category',
        'location',
    )
    search_fields = (
        'title',
        'text',
    )
    list_filter = (
        'category',
        'location',
        'author',
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'author',
    )
    search_fields = (
        'text',
    )
    list_filter = (
        'author',
    )


admin.site.register(Category)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
