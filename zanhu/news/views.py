#! /usr/bin/python3
# -*- coding:utf-8
# __author__ = '__Levvl__'

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,DeleteView
from django.template.loader import render_to_string
from django.http import HttpResponse,HttpResponseBadRequest,JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy

from zanhu.news.models import News
from zanhu.helpers import ajax_required,AuthorRequireMixin
class NewsListView(LoginRequiredMixin,ListView):
    """首页的动态"""
    model = News
    paginate_by = 20
    template_name = "news/news_list.html"

    def get_queryset(self):
        return News.objects.filter(reply=False)

class NewsDeleteView(LoginRequiredMixin,AuthorRequireMixin,DeleteView):
    model = News
    template_name = "news/news_confirm_delete.html"

    success_url = reverse_lazy("news:list")


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_new(request):
    """发送动态，AJAX POST请求"""
    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(user=request.user,content=post)
        html = render_to_string('news/news_single.html',{'news':posted,"request":request})
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest("内容不能为空")

@login_required
@ajax_required
@require_http_methods(['POST'])
def like(request):
    """给用户发表的动态点赞"""
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    news.switch_like(request.user)
    return JsonResponse({"likes":news.count_likers()})

@login_required
@ajax_required
@require_http_methods(['GET'])
def get_thread(request):
    news_id = request.GET['news']
    news = News.objects.get(pk=news_id)
    news_html = render_to_string("news/news_single.html",{"news":news})
    thread_html = render_to_string("news/news_thread.html",{"thread":news.get_thread()})
    return JsonResponse({
        "uuid":news_id,
        "news":news_html,
        "thread":thread_html,
    })

@login_required
@ajax_required
@require_http_methods(['POST'])
def port_comment(request):

    post = request.POST['reply'].strip()
    parent_id = request.POST['parent']
    parent = News.objects.get(pk=parent_id)
    if post:
        parent.reply_this(request.user, post)
        return JsonResponse({'comments': parent.comment_count()})
    else:
        return HttpResponseBadRequest("内容不能为空")










