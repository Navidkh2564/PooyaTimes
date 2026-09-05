from django.shortcuts import render

from news.models import News


def home(request):
    published_news = list(
        News.objects.published()
        .select_related('category', 'author')[:8]
    )
    featured_news = next(
        (news_item for news_item in published_news if news_item.is_featured),
        published_news[0] if published_news else None,
    )
    remaining_news = [
        news_item
        for news_item in published_news
        if featured_news is None or news_item.pk != featured_news.pk
    ]

    context = {
        'featured_news': featured_news,
        'secondary_news': remaining_news[0] if remaining_news else None,
        'strip_news': remaining_news[1:3],
        'archive_news': remaining_news[3:7],
    }
    return render(request, 'home/index.html', context)