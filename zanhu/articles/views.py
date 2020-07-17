#! /usr/bin/python3
# -*- coding:utf-8
# __author__ = '__Levvl__'

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,CreateView,UpdateView,DetailView
from django.urls import reverse_lazy
from django.contrib import messages

from zanhu.articles.models import Article
from zanhu.articles.forms import ArticleForm
from zanhu.helpers import AuthorRequireMixin

class ArticlesListView(LoginRequiredMixin,ListView):
    """已发布的文章列表"""

    model = Article
    paginate_by = 10
    context_object_name = "articles"
    template_name = 'articles/article_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self):
        return Article.objects.get_published()

class DraftListView(ArticlesListView):
    def get_queryset(self):
        return Article.objects.filter(user=self.request.user).get_drafts()

class ArticleCreateView(LoginRequiredMixin,CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_create.html"
    message = "您的文章已创建成功"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request,self.message)
        return reverse_lazy("articles:list")

class ArticleDetailView(LoginRequiredMixin,DetailView):
    """wen章 detail"""

    model = Article
    template_name = 'articles/article_detail.html'


class ArticleEditView(LoginRequiredMixin,AuthorRequireMixin,UpdateView):
    model = Article
    message = '您的文章已编辑'
    form_class = ArticleForm
    template_name = 'articles/article_update.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy("articles:article", kwargs={"slug": self.get_object().slug})

















