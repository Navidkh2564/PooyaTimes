from django.contrib import admin

from .models import Category, News, NewsAttachment, NewsContentBlock


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class NewsContentBlockInline(admin.StackedInline):
    model = NewsContentBlock
    extra = 1
    fields = ('position', 'text', 'image', 'caption')
    ordering = ('position',)
    verbose_name = 'بخش متن یا تصویر'
    verbose_name_plural = 'متن‌ها و تصاویر داخل خبر'


class NewsAttachmentInline(admin.TabularInline):
    model = NewsAttachment
    extra = 1
    fields = ('title', 'file')
    verbose_name = 'فایل پیوست'
    verbose_name_plural = 'فایل‌های قابل دانلود'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'author',
        'status',
        'is_featured',
        'published_at',
    )
    list_filter = ('status', 'is_featured', 'is_recommended', 'category')
    search_fields = ('title', 'summary', 'body', 'content_blocks__text')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('author',)
    date_hierarchy = 'published_at'
    list_select_related = ('category', 'author')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (NewsContentBlockInline, NewsAttachmentInline)
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'category', 'author', 'summary'),
        }),
        ('تصویر اصلی', {
            'fields': ('cover_image', 'image_url'),
        }),
        ('متن ساده', {
            'description': 'برای چیدمان آزاد متن و تصویر، به‌جای این کادر از بخش‌های محتوایی پایین صفحه استفاده کنید.',
            'fields': ('body',),
        }),
        ('انتشار', {
            'fields': (
                'status',
                'published_at',
                'reading_time',
                'is_featured',
                'is_recommended',
            ),
        }),
        ('اطلاعات سیستمی', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
