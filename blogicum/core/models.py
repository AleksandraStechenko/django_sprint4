from django.db import models


class BaseModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published.
    Добавляет дату и время публикации."""
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        abstract = True
