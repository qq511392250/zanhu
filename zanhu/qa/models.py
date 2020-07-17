#! /usr/bin/python3
# -*- coding:utf-8
# __author__ = '__Levvl__'

from __future__ import unicode_literals
import uuid
from collections import Counter

from slugify import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from taggit.managers import TaggableManager

from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation,GenericForeignKey


@python_2_unicode_compatible
class Vote(models.Model):
    """同时关联用户对问题以及回答的投票"""
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='qa_vote', verbose_name="用户")
    value = models.BooleanField(default=True, verbose_name="赞同或反对")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="votes_on")
    object_id = models.CharField(max_length=255)
    vote = GenericForeignKey()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "投票"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'content_type', 'object_id')
        index_together = ('content_type', 'object_id') #唯一索引


@python_2_unicode_compatible
class QuestionQuerySet(models.query.QuerySet):

    def get_answered(self):
        """已有回答的问题"""
        return self.filter(has_answer=True)

    def get_ununswered(self):
        """没有采纳回答的问题"""
        return self.filter(has_answer=False)

    def get_counted_tags(self):
        """统计所有问题中标签"""
        tag_dict = {}
        query = self.annotate(tagged=models.Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] +=1
        return tag_dict.items()


@python_2_unicode_compatible
class Question(models.Model):
    STATUS = (("O", "Open"), ("C", "Close"), ("D", "Draft"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='q_author', verbose_name="提问者")
    title = models.CharField(max_length=255,unique=True, verbose_name="标题")
    slug = models.SlugField(max_length=255, verbose_name="(问题)别名")
    status = models.CharField(max_length=1, choices=STATUS, default="O", verbose_name="问题状态")
    content = MarkdownxField(verbose_name="内容")
    tags = TaggableManager(help_text="多个标签使用，隔开", verbose_name="标签", )
    votes = GenericRelation(Vote, verbose_name='投票情况')
    has_answer = models.BooleanField(default=False, verbose_name="接收回答")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = "问题"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question,self).save(*args,**kwargs)

    def __str__(self):
        return self.title

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        dic = Counter(self.votes.values_list('value',flat=True))
        return dic[True]-dic[False]

    def get_answers(self):
        return Answer.objects.filter(question=self)


    def count_answers(self):
        return Answer.objects.filter(question=self).count()

    def get_upvoters(self):
        return [vote.user for vote in self.votes.fliter(value=True)]

    def get_downvoters(self):
        return [vote.user for vote in self.votes.fliter(value=False)]

    def get_accepted_answer(self):
        """被采纳的答案"""
        return Answer.objects.get(question=self, is_answer=True)


@python_2_unicode_compatible
class Answer(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='a_author',verbose_name="回答者")
    question = models.ForeignKey(Question,on_delete=models.CASCADE, verbose_name='被回答')
    content = MarkdownxField(verbose_name = "内容")
    is_answer = models.BooleanField(default=False, verbose_name='是否被采纳')
    votes = GenericRelation(Vote, verbose_name='投票情况')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ('-is_answer', '-created_at')
        verbose_name = "回答"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        dic = Counter(self.votes.values_list('value',flat=True))
        return dic[True]-dic[False]

    def get_upvoters(self):
        return [vote.user for vote in self.votes.fliter(value=True)]

    def get_downvoters(self):
        return [vote.user for vote in self.votes.fliter(value=False)]

    def accept_answer(self):
        answer_ser = Answer.objects.filter(question=self.question)
        answer_ser.update(is_answer=False)

        self.is_answer = True
        self.save()

        self.question.has_answer=True
        self.question.save()










