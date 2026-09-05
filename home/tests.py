from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import Category, News


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username='homepage-editor',
            password='test-password',
        )
        category = Category.objects.create(name='آموزش', slug='آموزش')
        cls.featured_news = News.objects.create(
            category=category,
            author=author,
            title='خبر ویژه صفحه اصلی',
            slug='خبر-ویژه-صفحه-اصلی',
            summary='خلاصه خبر ویژه',
            body='متن خبر ویژه',
            status=News.Status.PUBLISHED,
            published_at=timezone.now() - timedelta(minutes=30),
            is_featured=True,
        )

    def test_homepage_displays_featured_published_news(self):
        response = self.client.get(reverse('home:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.featured_news.title)
        self.assertContains(response, self.featured_news.get_absolute_url())

    def test_homepage_uses_reusable_layout(self):
        response = self.client.get(reverse('home:home'))

        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'includes/header.html')
        self.assertTemplateUsed(response, 'includes/footer.html')
