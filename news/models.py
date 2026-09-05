from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .validators import validate_attachment_size, validate_image_size


class Category(models.Model):
    name = models.CharField('نام', max_length=100, unique=True)
    slug = models.SlugField('نامک', max_length=120, unique=True, allow_unicode=True)
    description = models.TextField('توضیحات', blank=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

    def __str__(self):
        return self.name


class PublishedNewsQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status=News.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )


class News(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'پیش‌نویس'
        PUBLISHED = 'published', 'منتشرشده'

    category = models.ForeignKey(
        Category,
        verbose_name='دسته‌بندی',
        related_name='news_items',
        on_delete=models.PROTECT,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='نویسنده',
        related_name='news_items',
        on_delete=models.PROTECT,
    )
    title = models.CharField('عنوان', max_length=220)
    slug = models.SlugField('نامک', max_length=240, unique=True, allow_unicode=True)
    summary = models.TextField('خلاصه', max_length=600)
    body = models.TextField(
        'متن ساده خبر',
        blank=True,
        help_text='اگر از بخش‌های محتوایی پایین صفحه استفاده می‌کنید، این قسمت را خالی بگذارید.',
    )
    cover_image = models.ImageField(
        'تصویر اصلی',
        upload_to='news/covers/%Y/%m/',
        blank=True,
        validators=(validate_image_size,),
    )
    image_url = models.URLField(
        'نشانی تصویر خارجی',
        blank=True,
        help_text='تنها زمانی استفاده می‌شود که تصویر اصلی بارگذاری نشده باشد.',
    )
    reading_time = models.PositiveSmallIntegerField('زمان مطالعه', default=5)
    status = models.CharField(
        'وضعیت',
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField('زمان انتشار', blank=True, null=True)
    is_featured = models.BooleanField('خبر ویژه', default=False)
    is_recommended = models.BooleanField('پیشنهاد سردبیر', default=False)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    objects = PublishedNewsQuerySet.as_manager()

    class Meta:
        ordering = ('-published_at', '-created_at')
        indexes = [
            models.Index(fields=('status', 'published_at'), name='news_status_pub_idx'),
            models.Index(fields=('category', 'published_at'), name='news_category_pub_idx'),
        ]
        verbose_name = 'خبر'
        verbose_name_plural = 'خبرها'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})

    @property
    def author_display_name(self):
        return self.author.get_full_name() or self.author.get_username()

    @property
    def display_image_url(self):
        if self.cover_image:
            return self.cover_image.url
        return self.image_url


class NewsContentBlock(models.Model):
    news = models.ForeignKey(
        News,
        verbose_name='خبر',
        related_name='content_blocks',
        on_delete=models.CASCADE,
    )
    position = models.PositiveSmallIntegerField(
        'ترتیب نمایش',
        default=1,
        help_text='عدد کمتر، بخش را بالاتر نمایش می‌دهد.',
    )
    text = models.TextField('متن', blank=True)
    image = models.ImageField(
        'تصویر میان‌متن',
        upload_to='news/content/%Y/%m/',
        blank=True,
        validators=(validate_image_size,),
    )
    caption = models.CharField('توضیح تصویر', max_length=240, blank=True)

    class Meta:
        ordering = ('position', 'pk')
        verbose_name = 'بخش محتوایی'
        verbose_name_plural = 'بخش‌های محتوایی'

    def __str__(self):
        return f'{self.news} — بخش {self.position}'

    def clean(self):
        super().clean()
        has_text = bool(self.text.strip())
        has_image = bool(self.image)
        if has_text == has_image:
            raise ValidationError('در هر بخش دقیقاً یک متن یا یک تصویر وارد کنید.')
        if self.caption and not has_image:
            raise ValidationError({'caption': 'توضیح تصویر فقط برای بخش تصویری قابل استفاده است.'})


class NewsAttachment(models.Model):
    news = models.ForeignKey(
        News,
        verbose_name='خبر',
        related_name='attachments',
        on_delete=models.CASCADE,
    )
    title = models.CharField('عنوان فایل', max_length=160, blank=True)
    file = models.FileField(
        'فایل',
        upload_to='news/attachments/%Y/%m/',
        validators=(
            FileExtensionValidator(
                allowed_extensions=('pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip')
            ),
            validate_attachment_size,
        ),
    )
    uploaded_at = models.DateTimeField('زمان بارگذاری', auto_now_add=True)

    class Meta:
        ordering = ('uploaded_at',)
        verbose_name = 'فایل پیوست'
        verbose_name_plural = 'فایل‌های پیوست'

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.title or Path(self.file.name).name
