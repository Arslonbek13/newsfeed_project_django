from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView
from hitcount.utils import get_hitcount_model

from .models import News, Category
from .forms import ContactForm, CommentForm
from news_2.custom_permission import OnlyLoggedSuperUser
from hitcount.views import HitCountDetailView, HitCountMixin


# Create your views here.


def news_list(request):
    news_list = News.published.all()
    categories = Category.objects.all()
    context = {
        'news_list': news_list,
        'categories': categories
    }
    return render(request, "news/news_list.html", context)



def news_detail(request, news):
    news = get_object_or_404(News, slug=news, status=News.Status.Published)
    # news.view_count = news.view_count + 1
    # news.save()
    context = {}
    hit_count = get_hitcount_model().objects.get_for_object(news)
    hits = hit_count.hits
    hitcontext = context['hitcount'] = {'pk': hit_count.pk}
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if hit_count_response.hit_counted:
        hits = hits + 1
        hitcontext['hit_counted'] = hit_count_response.hit_counted
        hitcontext['hit_message'] = hit_count_response.hit_message
        hitcontext['total_hit'] = hits

    categories = Category.objects.all()
    news_list = News.published.all().order_by('-publish_time')[:15]
    local_one = News.published.filter(category__name='Local').order_by("-publish_time")
    local_news = News.published.all().filter(category__name='Local').order_by('-publish_time')[:5]
    comments = news.comments.filter(active=True)
    comment_count = comments.count()
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.news = news
            new_comment.user = request.user
            new_comment.save()
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    context = {
        'news': news,
        'news_list': news_list,
        'categories': categories,
        'local_one': local_one,
        'local_news': local_news,
        'comments': comments,
        'new_comment': new_comment,
        'comment_count': comment_count,
        'comment_form': comment_form
    }
    return render(request, 'news/news_detail.html', context)


# def homePageView(request):
#     categories = Category.objects.all()
#     news_list = News.published.all().order_by('-publish_time')[:15]
#     local_one = News.published.filter(category__name='Local').order_by("-publish_time")
#     local_news = News.published.all().filter(category__name='Local').order_by('-publish_time')[:5]
#     context = {
#         'news_list': news_list,
#         'categories': categories,
#         'local_one': local_one,
#         'local_news': local_news
#     }
#     return render(request, "news/index.html", context)


class HomePageView(ListView):
    model = News
    template_name = 'news/index.html'
    context_object_name = 'news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_list'] = News.published.all().order_by('-publish_time')[:15]
        # context['local_one'] = News.published.filter(category__name='Local').order_by("-publish_time")
        context['local_news'] = News.published.all().filter(category__name_en='Local').order_by('-publish_time')[:5]
        context['technology'] = News.published.all().filter(category__name_en='Technology').order_by('-publish_time')[:5]
        context['sport'] = News.published.all().filter(category__name_en='Sport').order_by('-publish_time')[:5]
        context['world'] = News.published.all().filter(category__name_en='World').order_by('-publish_time')[:5]
        return context



# def contactPageView(request):
#     form = ContactForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         form.save()
#         return HttpResponse('<h2>Thank you for contact us.</h2>')
#     context = {
#         "form": form
#     }
#     return render(request, 'news/contact.html', context)




class ContactPageView(TemplateView):
    template_name = 'news/contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        context = {
            "form": form
        }
        return render(request, 'news/contact.html', context)

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return HttpResponse('<h2>Thank you for contact us.</h2>')
        context = {
            "form": form
        }
        return render(request, 'news/contact.html', context)



def errorPageView(request):
    context = {

    }
    return render(request, 'news/404.html', context)


class LocalNewsView(ListView):
    model = News
    template_name = 'news/local.html'
    context_object_name = 'local_news'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='local')
        return news

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_list'] = News.published.all().order_by('-publish_time')[:15]
        context['local_news'] = News.published.all().filter(category__name='Local').order_by('-publish_time')[:5]
        return context



class WorldNewsView(ListView):
    model = News
    template_name = 'news/world.html'
    context_object_name = 'world_news'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='world')
        return news

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_list'] = News.published.all().order_by('-publish_time')[:15]
        context['world'] = News.published.all().filter(category__name='World').order_by('-publish_time')[:5]
        return context



class TechnologyNewsView(ListView):
    model = News
    template_name = 'news/technology.html'
    context_object_name = 'technology_news'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='technology')
        return news

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_list'] = News.published.all().order_by('-publish_time')[:15]
        context['technology'] = News.published.all().filter(category__name='Technology').order_by('-publish_time')[:5]
        return context



class SportNewsView(ListView):
    model = News
    template_name = 'news/sport.html'
    context_object_name = 'sport_news'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name='sport')
        return news

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_list'] = News.published.all().order_by('-publish_time')[:15]
        context['sport'] = News.published.all().filter(category__name='Sport').order_by('-publish_time')[:5]
        return context



class NewsUpdateView(OnlyLoggedSuperUser, UpdateView):
    model = News
    fields = ('title', 'body', 'image', 'category', 'status')
    template_name = 'crud/news_edit.html'



class NewsDeleteView(OnlyLoggedSuperUser, DeleteView):
    model = News
    template_name = 'crud/news_delete.html'
    success_url = reverse_lazy('home_page')



class NewsCreateView(OnlyLoggedSuperUser, CreateView):
    model = News
    template_name = 'crud/news_create.html'
    fields = ('title', 'title_en', 'title_uz', 'title_ru',
              'slug', 'body', 'body_en', 'body_uz', 'body_ru',
              'image', 'category', 'status')
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_page_view(request):
    admin_users = User.objects.filter(is_superuser=True)
    categories = Category.objects.all()

    context = {
        'admin_users': admin_users,
        'categories': categories
    }
    return render(request, 'pages/admin_page.html', context)


class SearchResultsList(ListView):
    model = News
    template_name = 'news/search_result.html'
    context_object_name = 'all_news'

    def get_queryset(self):
        query = self.request.GET.get('s')
        return News.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context