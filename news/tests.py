from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, News, NewsContentBlock


class NewsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username='editor',
            password='test-password',
            first_name='مریم',
            last_name='احمدی',
        )
        cls.category = Category.objects.create(name='کنکور', slug='کنکور')
        cls.published_news = News.objects.create(
            category=cls.category,
            author=cls.author,
            title='خبر منتشرشده',
            slug='خبر-منتشرشده',
            summary='خلاصه خبر منتشرشده',
            body='متن کامل خبر منتشرشده',
            status=News.Status.PUBLISHED,
            published_at=timezone.now() - timedelta(hours=1),
            is_featured=True,
        )
        cls.draft_news = News.objects.create(
            category=cls.category,
            author=cls.author,
            title='خبر پیش‌نویس',
            slug='خبر-پیش‌نویس',
            summary='خلاصه خبر پیش‌نویس',
            body='متن کامل خبر پیش‌نویس',
        )
        cls.future_news = News.objects.create(
            category=cls.category,
            author=cls.author,
            title='خبر آینده',
            slug='خبر-آینده',
            summary='خلاصه خبر آینده',
            body='متن کامل خبر آینده',
            status=News.Status.PUBLISHED,
            published_at=timezone.now() + timedelta(days=1),
        )

    def test_published_manager_hides_drafts_and_future_news(self):
        self.assertQuerySetEqual(
            News.objects.published(),
            [self.published_news],
        )

    def test_news_list_only_shows_published_news(self):
        response = self.client.get(reverse('news:list'))

        self.assertContains(response, self.published_news.title)
        self.assertNotContains(response, self.draft_news.title)
        self.assertNotContains(response, self.future_news.title)

    def test_news_detail_uses_unicode_slug(self):
        response = self.client.get(self.published_news.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_news.body)

    def test_ordered_content_blocks_render_on_detail_page(self):
        NewsContentBlock.objects.create(
            news=self.published_news,
            position=1,
            text='متن بخش اول خبر',
        )
        NewsContentBlock.objects.create(
            news=self.published_news,
            position=2,
            text='متن بخش دوم خبر',
        )

        response = self.client.get(self.published_news.get_absolute_url())

        self.assertContains(response, 'متن بخش اول خبر')
        self.assertContains(response, 'متن بخش دوم خبر')

    def test_content_block_requires_exactly_one_content_type(self):
        block = NewsContentBlock(news=self.published_news, text='')

        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_draft_detail_returns_not_found(self):
        response = self.client.get(self.draft_news.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_search_filters_news(self):
        response = self.client.get(reverse('news:list'), {'q': 'منتشرشده'})

        self.assertContains(response, self.published_news.title)
        self.assertNotContains(response, self.draft_news.title)
