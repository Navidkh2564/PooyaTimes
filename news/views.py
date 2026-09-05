from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Category, News


class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_items'
    paginate_by = 12

    def get_queryset(self):
        queryset = News.objects.published().select_related('category', 'author')
        query = self.request.GET.get('q', '').strip()
        category_slug = self.request.GET.get('category', '').strip()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(body__icontains=query)
            )
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['query'] = self.request.GET.get('q', '').strip()
        context['selected_category'] = self.request.GET.get('category', '').strip()
        return context


class NewsDetailView(DetailView):
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news_item'

    def get_queryset(self):
        return (
            News.objects.published()
            .select_related('category', 'author')
            .prefetch_related('content_blocks', 'attachments')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_news'] = (
            News.objects.published()
            .filter(category=self.object.category)
            .exclude(pk=self.object.pk)
            .select_related('category', 'author')[:3]
        )
        return context
