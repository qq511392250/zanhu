#! /usr/bin/python3
# -*- coding:utf-8
# __author__ = '__Levvl__'
from django.urls import path

from zanhu.news import views

app_name = "news"
urlpatterns = [
    path("", views.NewsListView.as_view(), name="list"),
    path("post-news/",views.post_new, name ='post_news'),
    path("delete/<str:pk>/", views.NewsDeleteView.as_view(), name="delete_news"),
    path("like/",views.like, name ='like_post'),
    path('get-thread/',views.get_thread, name='get_thread'),
    path('post-comment/', views.port_comment, name='post_comments'),

]
